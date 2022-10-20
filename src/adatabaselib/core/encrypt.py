import uuid

# Генерация uuid-кода тикета:
def get_uuid() -> str:
	return uuid.uuid4().hex
