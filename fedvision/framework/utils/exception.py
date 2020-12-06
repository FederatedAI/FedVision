class FedvisionBaseException(BaseException):
    ...


class FedvisionException(FedvisionBaseException, Exception):
    ...


class FedvisionExtensionException(FedvisionException):
    ...


class FedvisionWorkerException(FedvisionException):
    ...


class FedvisionJobCompileException(FedvisionException):
    ...


class FedvisionDataNotFoundException(FedvisionException):
    ...
