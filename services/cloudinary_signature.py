import cloudinary
import datetime


def get_signature():
    return cloudinary.utils.sign_request({"timestamp": datetime.datetime.timestamp(datetime.datetime.utcnow())},
                                         {"api_key": "372331583124665",
                                          "api_secret": "0Gor7f2q1TEYq2GB3pKD227oG4I"})
