import enum
import hmac

class constants(enum.Enum):
    '''
    Enum class, contains all the necessary constants required/used by the Binance data pipeline
    '''
    ssl_cert = (None or get_conf('x-amz-ssl', 'ssl-cert', None))
    ssl_verify_server = (get_conf_bool('x-amz-ssl', 'ssl-verify-server', False))
    api_endpoint = 'https://api.binance.com'
    api_key = get_value()[0]
    api_secret = get_value()[1]
    klines_params = {'symbol': 'BTCUSDT','interval' : '1m'}
    klines_api_relative_path = '/api/v3/klines' #according to swagger: https://binance.github.io/binance-api-swagger/#/Trade/get_api_v3_allOrders
    accountOrders_api_relative_path = '/api/v3/allOrders' #according to swagger: https://binance.github.io/binance-api-swagger/#/Trade/get_api_v3_allOrders
    accountOrders_Params = {'symbol': 'BTCUSDT' , 'signature' : get_sign()} #Defaults to 500 limit per call.


def get_sign() -> str:
	'''
	get an uuid for the signature
	'''
	return hmac.new(constants.api_secret, query.encode("utf-8"),hashlib.sha256).hexdigest()

def get_value(stage=None) -> Obj:
	"""
	Gets the value of a secret.

	:param stage: The stage of the secret to retrieve. If this is None, the
			current stage is retrieved.
	:return: The value of the secret. When the secret is a string, the value is
			contained in the `SecretString` field. When the secret is bytes,
			it is contained in the `SecretBinary` field.
	"""
	if self.name is None:
		raise ValueError

	try:
		kwargs = {'SecretId': self.name}
		if stage is not None:
		kwargs['VersionStage'] = stage
		response = self.secretsmanager_client.get_secret_value(**kwargs)
		logger.info("Got value for secret %s.", self.name)
	except ClientError:
		logger.exception("Couldn't get value for secret %s.", self.name)
		raise
	else:
		return response