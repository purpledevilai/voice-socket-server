connections = {}


def create_new_connection(context_id):
    connections[context_id] = {
        "first_sample_time_stamp": None,
        "last_sample_time_stamp": None,
        "total_samples": 0,
        "pcm_samples": [],
        "sample_rate": 16000
    }
