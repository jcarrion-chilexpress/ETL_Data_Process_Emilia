
KEYWORDS = ["cas-", "reclamo", "atrasado", "perdido", "robado"]
URGENCY_PATTERNS = [
    r"urgent",
    r"inmediat",
    r"rapido|rápido",
    r"hoy mismo",
    r"sin respuesta",
    r"demor",
    r"atrasad",
    r"incumplimiento",]

CONFUSION_PATTERNS = [
    r"no entiendo",
    r"confus",
    r"que debo",
    r"como puedo",
    r"no me queda claro",]

SATISFACTION_PATTERNS = [
    r"\bgracias\b",
    r"perfecto",
    r"excelente",
    r"genial",
    r"muchas gracias",
    r"listo gracias",]

FRUSTRACION = [
    r"no entiendo",
    r"no comprendo",
    r"no me ayud",
    r"no sirve",
    r"no funciona",
    r"mal servicio",
    r"pesimo",
    r"p[eé]simo",
    r"frustrad",
    r"enojad",
    r"molest",
    r"harto",
    r"inutil",
    r"bot est[uú]pido",
    r"no responde",
    r"otra vez",
    r"ya te (dije|di)",
    r"insisto",
    r"hablar con (una )?persona",
    r"ejecutivo",
    r"humano",]

LOOP_TRACKING = [
    r"estado de mi env[ií]o",
    r"revisar el estado",
    r"n[uú]mero de.*ot",
    r"orden de transporte",]

BOT_PIDE_OT = (
    "orden de transporte",
    "numero de ot",
    "número de ot",
    "al menos 10",
    "10 digitos",
    "10 dígitos",)

ERROR_BOT_PATTERNS = [
    r"no logr[eé] entender",
    r"error (al|en) (procesar|consultar)",
    r"fall[oó] (la|el) (consulta|servicio)",]

