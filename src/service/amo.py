import http
import requests
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from sharq_models import PassportData #type: ignore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Gender(Enum):
    MALE = "1"
    FEMALE = "2"


class EducationLanguage(Enum):
    UZBEK = "1"
    RUSSIAN = "2"
    ENGLISH = "3"


CONTACT_FIELD_MAPPINGS = {
    "phone": "PHONE",
    "email": "EMAIL",
    "ism": "ism",
    "familya": "familya",
    "ota ismi": "ota ismi",
    "должность": "должность",
    "tug'ilgan kuni": "tug'ilgan kuni",
    "jinsi": "jinsi",
    "country": "country",
    "region": "region",
    "district": "district",
    "manzil": "manzil",
}

DEAL_FIELD_MAPPINGS = {
    "talim tili": "talim tili",
    "talim turi": "talim turi",
    "talim shakli": "talim shakli",
    "talim yo'nalishi": "talim yo'nalishi",
    "o'rta talim tugatgan yili": "o'rta talim tugatgan yili",
    "admission id": "admission id",
    "certificate fayl": "certificate fayl",
    "pasport fayl": "pasport fayl",
}

FIELD_CODE_FIELDS = {"phone", "email"}

PIPELINE_TYPES = {
    "FIRST_CREATE": "first_create",
    "LEAD_ACCEPTED": "lead_accepted",
    "LEAD_REJECTED": "lead_rejected",
    "GET_CONTRACT": "get_contract",
}


@dataclass
class ContactData:
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    middle_name: Optional[str] = None
    position: Optional[str] = None
    birthdate: Optional[str] = None
    gender: Optional[Gender] = None
    country: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None


@dataclass
class DealData:
    name: str
    contact_id: int
    edu_lang_id: str
    edu_type: str
    edu_form: str
    edu_direction: str
    edu_end_date: str
    admission_id: int
    certificate_link: str
    passport_file_link: str
    price: float = 0


class AmoCRMConfig:
    def __init__(self, config_data: Dict[str, Any]):
        self.base_api = config_data.get("base_url")
        self.token = config_data.get("token")

        self.pipelines = {
            PIPELINE_TYPES["FIRST_CREATE"]: {
                "pipeline_id": config_data.get("first_create_pipline_id"),
                "status_id": config_data.get("first_create_status_id"),
            },
            PIPELINE_TYPES["LEAD_ACCEPTED"]: {
                "pipeline_id": config_data.get("lead_accepted_pipline_id"),
                "status_id": config_data.get("lead_accepted_status_id"),
            },
            PIPELINE_TYPES["LEAD_REJECTED"]: {
                "pipeline_id": config_data.get("lead_rejected_pipline_id"),
                "status_id": config_data.get("lead_rejected_status_id"),
            },
            PIPELINE_TYPES["GET_CONTRACT"]: {
                "pipeline_id": config_data.get("get_contract_pipline_id"),
                "status_id": config_data.get("get_contract_status_id"),
            },
        }

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }


class AmoCRMException(Exception):
    pass


class FieldBuilder:
    @staticmethod
    def create_field_value(
        field_id: str, value: Any, use_field_code: bool = False
    ) -> Dict[str, Any]:
        field_key = "field_code" if use_field_code else "field_id"
        return {field_key: field_id, "values": [{"value": value}]}

    @staticmethod
    def build_fields_from_mappings(
        mappings: List[Tuple[str, Optional[str], Any]], field_mappings: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Build field values from mappings using a generic approach"""
        fields = []

        for field_name, field_id, value in mappings:
            if field_id is None or value is None:
                continue

            use_field_code = field_name in FIELD_CODE_FIELDS
            fields.append(
                FieldBuilder.create_field_value(field_id, value, use_field_code)
            )

        return fields


class AmoCRMService:
    def __init__(self, config: AmoCRMConfig):
        self.config = config
        self._contact_fields_cache: Optional[Dict[str, int]] = None
        self._lead_fields_cache: Optional[Dict[str, int]] = None

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Union[Dict, List]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.config.base_api}/{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.config.headers,
                params=params,
                json=json_data,
            )
            response.raise_for_status()

            if response.status_code == http.HTTPStatus.NO_CONTENT:
                return {}

            return response.json()

        except requests.exceptions.RequestException as e:
            self._handle_request_error(e, method, endpoint)

    def _handle_request_error(
        self, error: Exception, method: str, endpoint: str
    ) -> None:
        error_msg = f"API request failed for {method} {endpoint}: {error}"
        if hasattr(error, "response") and error.response is not None:
            error_msg += f" | Status: {error.response.status_code} | Response: {error.response.text}"

        logger.error(error_msg)
        raise AmoCRMException(error_msg)

    def _get_embedded_data(
        self, data: Dict[str, Any], entity_type: str
    ) -> List[Dict[str, Any]]:
        return data.get("_embedded", {}).get(entity_type, [])

    def _get_first_entity(
        self, data: Dict[str, Any], entity_type: str
    ) -> Optional[Dict[str, Any]]:
        entities = self._get_embedded_data(data, entity_type)
        return entities[0] if entities else None

    def get_status_by_id(
        self, pipeline_id: int, status_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            data = self._make_request("GET", f"leads/pipelines/{pipeline_id}")
            statuses = self._get_embedded_data(data, "statuses")

            status = next((item for item in statuses if item["id"] == status_id), None)

            if not status:
                logger.warning(
                    f"Status ID {status_id} not found in pipeline {pipeline_id}"
                )
                return None

            return status

        except AmoCRMException:
            logger.error(
                f"Failed to get status for pipeline {pipeline_id}, status {status_id}"
            )
            return None

    def search_contact(self, phone: str) -> Optional[Dict[str, Any]]:
        try:
            data = self._make_request("GET", "contacts", params={"query": phone})
            contact = self._get_first_entity(data, "contacts")

            if not contact:
                logger.info(f"Contact not found for phone: {phone}")
                return None

            return contact

        except AmoCRMException:
            logger.error(f"Failed to search contact with phone: {phone}")
            return None

    def _get_cached_fields(self, endpoint: str, cache_attr: str) -> Dict[str, int]:
        cache = getattr(self, cache_attr)
        if cache is None:
            try:
                data = self._make_request("GET", endpoint)
                fields = self._get_embedded_data(data, "custom_fields")

                cache = {field["name"].lower(): field["id"] for field in fields}
                setattr(self, cache_attr, cache)

            except AmoCRMException:
                logger.error(f"Failed to get {endpoint} custom fields")
                cache = {}
                setattr(self, cache_attr, cache)

        return cache

    def _get_contact_fields(self) -> Dict[str, int]:
        return self._get_cached_fields(
            "contacts/custom_fields", "_contact_fields_cache"
        )

    def _get_lead_fields(self) -> Dict[str, int]:
        return self._get_cached_fields("leads/custom_fields", "_lead_fields_cache")

    def _build_contact_fields_values(
        self, contact_data: ContactData
    ) -> List[Dict[str, Any]]:
        fields = self._get_contact_fields()

        field_mappings = [
            ("phone", CONTACT_FIELD_MAPPINGS["phone"], contact_data.phone),
            ("email", CONTACT_FIELD_MAPPINGS["email"], contact_data.email),
            ("ism", fields.get(CONTACT_FIELD_MAPPINGS["ism"]), contact_data.first_name),
            (
                "familya",
                fields.get(CONTACT_FIELD_MAPPINGS["familya"]),
                contact_data.last_name,
            ),
            (
                "ota ismi",
                fields.get(CONTACT_FIELD_MAPPINGS["ota ismi"]),
                contact_data.middle_name,
            ),
            (
                "должность",
                fields.get(CONTACT_FIELD_MAPPINGS["должность"]),
                contact_data.position,
            ),
            (
                "tug'ilgan kuni",
                fields.get(CONTACT_FIELD_MAPPINGS["tug'ilgan kuni"]),
                contact_data.birthdate,
            ),
            (
                "jinsi",
                fields.get(CONTACT_FIELD_MAPPINGS["jinsi"]),
                contact_data.gender if contact_data.gender else None,
            ),
            (
                "country",
                fields.get(CONTACT_FIELD_MAPPINGS["country"]),
                contact_data.country,
            ),
            (
                "region",
                fields.get(CONTACT_FIELD_MAPPINGS["region"]),
                contact_data.region,
            ),
            (
                "district",
                fields.get(CONTACT_FIELD_MAPPINGS["district"]),
                contact_data.district,
            ),
            (
                "manzil",
                fields.get(CONTACT_FIELD_MAPPINGS["manzil"]),
                contact_data.address,
            ),
        ]

        return FieldBuilder.build_fields_from_mappings(
            field_mappings, CONTACT_FIELD_MAPPINGS
        )

    def _format_to_amocrm_date(self, date_str: str) -> str:
        if date_str == "":
            return f"0000-00-00T00:00:00+05:00"
        return f"{date_str}T00:00:00+05:00"

    def _build_deal_fields_values(self, deal_data: DealData) -> List[Dict[str, Any]]:
        fields = self._get_lead_fields()

        field_mappings = [
            (
                "talim tili",
                fields.get(DEAL_FIELD_MAPPINGS["talim tili"]),
                deal_data.edu_lang_id,
            ),
            (
                "talim turi",
                fields.get(DEAL_FIELD_MAPPINGS["talim turi"]),
                deal_data.edu_type,
            ),
            (
                "talim shakli",
                fields.get(DEAL_FIELD_MAPPINGS["talim shakli"]),
                deal_data.edu_form,
            ),
            (
                "talim yo'nalishi",
                fields.get(DEAL_FIELD_MAPPINGS["talim yo'nalishi"]),
                deal_data.edu_direction,
            ),
            (
                "o'rta talim tugatgan yili",
                fields.get(DEAL_FIELD_MAPPINGS["o'rta talim tugatgan yili"]),
                self._format_to_amocrm_date(deal_data.edu_end_date),
            ),
            (
                "admission id",
                fields.get(DEAL_FIELD_MAPPINGS["admission id"]),
                str(deal_data.admission_id),
            ),
            (
                "certificate fayl",
                fields.get(DEAL_FIELD_MAPPINGS["certificate fayl"]),
                deal_data.certificate_link,
            ),
            (
                "pasport fayl",
                fields.get(DEAL_FIELD_MAPPINGS["pasport fayl"]),
                deal_data.passport_file_link,
            ),
        ]

        return FieldBuilder.build_fields_from_mappings(
            field_mappings, DEAL_FIELD_MAPPINGS
        )

    def _create_or_update_contact(self, contact_data: ContactData) -> Optional[int]:
        existing_contact = self.search_contact(contact_data.phone)
        custom_fields_values = self._build_contact_fields_values(contact_data)
        contact_name = f"{contact_data.last_name} {contact_data.first_name}"

        if existing_contact:
            contact_id = existing_contact["id"]
            logger.info(f"Updating existing contact: {contact_id}")

            self._make_request(
                "PATCH",
                f"contacts/{contact_id}",
                json_data={
                    "name": contact_name,
                    "custom_fields_values": custom_fields_values,
                },
            )

            return contact_id
        else:
            logger.info("Creating new contact")

            data = self._make_request(
                "POST",
                "contacts",
                json_data=[
                    {
                        "name": contact_name,
                        "custom_fields_values": custom_fields_values,
                    }
                ],
            )

            created_contact = self._get_first_entity(data, "contacts")
            contact_id = created_contact.get("id") if created_contact else None

            logger.info(f"Contact created successfully: {contact_id}")
            return contact_id

    def create_contact(self, contact_data: ContactData) -> Optional[int]:
        try:
            return self._create_or_update_contact(contact_data)
        except AmoCRMException as e:
            logger.error(f"Failed to create/update contact: {e}")
            return None

    def _create_deal_with_pipeline(
        self, deal_data: DealData, pipeline_type: str, tags: List[str]
    ) -> Optional[Dict[str, Any]]:
        custom_fields_values = self._build_deal_fields_values(deal_data)
        pipeline_config = self.config.pipelines[pipeline_type]

        deal_request_data = [
            {
                "name": deal_data.name,
                "pipeline_id": pipeline_config["pipeline_id"],
                "status_id": pipeline_config["status_id"],
                "_embedded": {
                    "contacts": [{"id": deal_data.contact_id}],
                    "tags": [{"name": tag} for tag in tags],
                },
                "custom_fields_values": custom_fields_values,
            }
        ]

        data = self._make_request("POST", "leads", json_data=deal_request_data)
        created_deal = self._get_first_entity(data, "leads")

        if created_deal:
            deal_id = created_deal.get("id")
            logger.info(f"Deal created successfully: {deal_id}")

        return created_deal

    def create_deal(self, deal_data: DealData) -> Optional[Dict[str, Any]]:
        try:
            return self._create_deal_with_pipeline(
                deal_data, PIPELINE_TYPES["FIRST_CREATE"], ["Qabul sayt"]
            )
        except AmoCRMException as e:
            logger.error(f"Failed to create deal: {e}")
            return None

    def update_lead_status(
        self, pipeline_id: int, status_id: int, lead_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            data = self._make_request(
                "PATCH",
                f"leads/{lead_id}",
                json_data={
                    "pipeline_id": int(pipeline_id),
                    "status_id": int(status_id),
                },
            )

            logger.info(f"Lead {lead_id} status updated successfully")
            return data

        except AmoCRMException as e:
            logger.error(f"Failed to update lead status: {e}")
            return None

    def _update_lead_with_pipeline(self, lead_id: int, pipeline_type: str) -> bool:
        pipeline_config = self.config.pipelines[pipeline_type]
        result = self.update_lead_status(
            pipeline_config["pipeline_id"], pipeline_config["status_id"], lead_id
        )
        return result is not None
    
    def move_lead_to_get_contact(self, lead_id: int) -> bool:
        return self._update_lead_with_pipeline(lead_id, PIPELINE_TYPES["GET_CONTRACT"])

    def accept_lead(self, lead_id: int) -> bool:
        return self._update_lead_with_pipeline(lead_id, PIPELINE_TYPES["LEAD_ACCEPTED"])

    def reject_lead(self, lead_id: int) -> bool:
        return self._update_lead_with_pipeline(lead_id, PIPELINE_TYPES["LEAD_REJECTED"])

    def _create_initial_contact(self, phone: str) -> Optional[int]:
        existing_contact = self.search_contact(phone)

        if existing_contact:
            contact_id = existing_contact["id"]
            logger.info(f"Contact already exists with phone {phone}: {contact_id}")
            return contact_id

        contact_name = f"Unknown User ({phone})"
        contact_data = [
            {
                "name": contact_name,
                "custom_fields_values": [
                    {"field_code": "PHONE", "values": [{"value": phone}]}
                ],
            }
        ]

        data = self._make_request("POST", "contacts", json_data=contact_data)
        created_contact = self._get_first_entity(data, "contacts")
        contact_id = created_contact.get("id") if created_contact else None

        logger.info(f"Initial contact created: {contact_id}")
        return contact_id

    def create_initial_contact_with_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        try:
            contact_id = self._create_initial_contact(phone)
            if not contact_id:
                return None

            deal_name = f"Yangi Lead - {phone}"
            deal_data = DealData(
                name=deal_name,
                contact_id=contact_id,
                edu_lang_id="",
                edu_type="",
                edu_form="",
                edu_direction="",
                edu_end_date="",
                admission_id=0,
                certificate_link="",
                passport_file_link="",
            )

            created_deal = self._create_deal_with_pipeline(
                deal_data, PIPELINE_TYPES["FIRST_CREATE"], ["Qabul sayt - Yangi Lead"]
            )

            if created_deal:
                deal_id = created_deal.get("id")
                logger.info(f"Initial deal created: {deal_id}")

                return {"contact_id": contact_id, "deal_id": deal_id, "is_new": True}

            return None

        except AmoCRMException as e:
            logger.error(
                f"Failed to create initial contact/deal with phone {phone}: {e}"
            )
            return None

    def update_lead_with_passport_data(
        self, deal_id: int, contact_id: int, contact_data: ContactData
    ) -> bool:
        try:
            custom_fields_values = self._build_contact_fields_values(contact_data)
            contact_name = f"{contact_data.last_name.upper()} {contact_data.first_name.upper()}"

            self._make_request(
                "PATCH",
                f"contacts/{contact_id}",
                json_data={
                    "name": contact_name,
                    "custom_fields_values": custom_fields_values,
                },
            )
            
            self._make_request(
                "PATCH",
                f"leads/{deal_id}",
                json_data={
                    "_embedded": {
                        "contacts": [{"id": contact_id}],
                        "tags": [{"name": "Qabul sayt - Passport Ma'lumotlari"}],
                    },
                },
            )

            return True

        except AmoCRMException as e:
            logger.error(f"Failed to update lead with passport data: {e}")
            return False

    def update_contact_with_full_data(self, deal_id: int, deal_data: DealData) -> bool:
        try:
            custom_fields_values = self._build_deal_fields_values(deal_data)

            self._make_request(
                "PATCH",
                f"leads/{deal_id}",
                json_data={
                    "name": deal_data.name,
                    "price": int(deal_data.price),
                    "custom_fields_values": custom_fields_values,
                },
            )

            logger.info(f"Deal {deal_id} updated with full data")

            # Accept lead
            if self.accept_lead(deal_id):
                logger.info("Lead accepted successfully")

            return True

        except AmoCRMException as e:
            logger.error(f"Failed to update contact/deal with full data: {e}")
            return False


def create_amocrm_service(config_data: Dict[str, Any]) -> AmoCRMService:
    config = AmoCRMConfig(config_data)
    return AmoCRMService(config)


def create_initial_lead(
    phone: str, config_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    try:
        amo_service = create_amocrm_service(config_data)
        return amo_service.create_initial_contact_with_phone(phone)
    except Exception as e:
        logger.error(f"Failed to create initial lead: {e}")
        return None


def update_lead_with_passport_data(
    deal_id: int, contact_id: int, passport_data: PassportData, config_data: Dict[str, Any]
) -> bool:
    contact_data = ContactData(
        first_name=passport_data.first_name,
        last_name=passport_data.last_name,
        middle_name=passport_data.third_name,
        gender=passport_data.gender,
    )
    try:
        amo_service = create_amocrm_service(config_data)
        return amo_service.update_lead_with_passport_data(deal_id, contact_id, contact_data)
    except Exception as e:
        logger.error(f"Failed to update lead with passport data: {e}")
        return False


def update_lead_with_full_data(
    deal_id: int, deal_data: DealData, config_data: Dict[str, Any]
) -> bool:
    try:
        amo_service = create_amocrm_service(config_data)
        return amo_service.update_contact_with_full_data(deal_id, deal_data)
    except Exception as e:
        logger.error(f"Failed to update lead with full data: {e}")
        return False
