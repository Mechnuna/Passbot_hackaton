import abc
from models.enums import Roles


class TelegramUser:
	def __init__(self, tg_name: str) -> None:
		self.__tg_name = tg_name

	@property
	def tg_name(self):
		return self.__tg_name


class BaseUser:
	def __init__(self, first_name: str, last_name: str, patr_name: str) -> None:
		assert ((first_name is not None) and isinstance(first_name, str))
		assert ((last_name is not None) and isinstance(first_name, str))

		if patr_name is not None:
			assert isinstance(patr_name, str)

		self.__first_name = first_name
		self.__last_name = last_name
		self.__patr_name = patr_name
		self.__full_name = self.__build_full_name()

	def __build_full_name(self):
		full_name = self.__last_name + " " + self.__first_name
		if self.___patr_name is not None:
			full_name += " " + self.__patr_name

	@property
	def first_name(self):
		return self.__first_name

	@property
	def last_name(self):
		return self.__last_name

	@property
	def patr_name(self):
		return self.__patr_name

	@property
	def full_name(self):
		return self.__full_name


class GuestUser(BaseUser):
	def __init__(self, first_name: str, last_name: str, patr_name: str, guest_type) -> None:
		super().__init__(first_name, last_name, patr_name)
		self.__guest_type = guest_type

	@property
	def guest_type(self):
		return self.__guest_type


class InvitingInterface(abc.ABC):
	@property
	@abc.abstractmethod
	def is_in_school(self) -> bool:
		pass

	@property
	@abc.abstractmethod
	def has_role(self) -> Roles:
		pass
	
	@property
	@abc.abstractmethod
	def is_self_approved(self) -> bool:
		pass

	@property
	@abc.abstractmethod
	def is_self_responsible(self) -> bool:
		pass

	@property
	@abc.abstractmethod
	def is_able_unloading(self) -> bool:
		pass

	@property
	@abc.abstractmethod
	def has_unlimited_booking(self) -> bool:
		pass
	
	@property
	@abc.abstractmethod
	def max_people_to_book() -> int:
		pass


class RoleLearner(InvitingInterface):
	@property
	def is_in_school(self) -> bool:
		return True


	@property
	def has_role(self):
		return Roles.LEARNER.value
	
	@property
	def is_self_approved(self) -> bool:
		return True
	
	@property
	def is_self_responsible(self) -> bool:
		return True
	
	@property
	def is_able_unloading(self) -> bool:
		return False
	
	@property
	def has_unlimited_booking(self) -> bool:
		return False
	
	@property
	def max_people_to_book(self) -> int:
		return 2


class RoleAdm(InvitingInterface):
	@property
	def is_in_school(self) -> bool:
		return True

	@property
	def has_role(self) -> Roles:
		return Roles.ADM.value

	@property	
	def is_self_approved(self) -> bool:
		return True
	
	@property
	def is_self_responsible(self) -> bool:
		return True
	
	@property
	def is_able_unloading(self) -> bool:
		return True
	
	@property
	def has_unlimited_booking(self) -> bool:
		return True
	
	@property
	def max_people_to_book(self) -> int:
		return 100


class RoleOutsider(InvitingInterface):
	@property
	def is_in_school(self) -> bool:
		return False
	
	@property
	def has_role(self) -> Roles:
		return Roles.OUTSIDER.value

	@property	
	def is_self_approved(self) -> bool:
		return False
	
	@property
	def is_self_responsible(self) -> bool:
		return False
	
	@property
	def is_able_unloading(self) -> bool:
		return False
	
	@property
	def has_unlimited_booking(self) -> bool:
		return False
	
	@property
	def max_people_to_book(self) -> int:
		return 1


def get_role(role: Roles):
	if role == Roles.ADM.value:
		return RoleAdm()
	elif role == Roles.LEARNER.value:
		return RoleLearner()
	else:
		return RoleOutsider()

