"""Application constants."""

# Risk thresholds
RISK_THRESHOLD_HIGH = 80
RISK_THRESHOLD_MEDIUM = 50
RISK_THRESHOLD_LOW = 20

# Risk levels
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]

# High risk amount threshold
HIGH_RISK_AMOUNT_THRESHOLD = 10000

# Medium risk device score
MEDIUM_RISK_DEVICE_SCORE = 0.6

# Default top k for retrieval
DEFAULT_TOP_K_RETRIEVAL = 5

# Transaction limits
MAX_TRANSACTION_AMOUNT = 1000000
MIN_TRANSACTION_AMOUNT = 0.01

# API settings
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Supported currencies
SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY"]

# Transaction types
TRANSACTION_TYPES = ["transfer", "payment", "withdrawal", "deposit", "investment"]

# Compliance regulations
REGULATION_TYPES = ["AML", "KYC", "GDPR", "SEC", "FATF"]
