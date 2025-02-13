from stores.connections import connections


def handle_print_sample_rate(data):
    context_id = data["context_id"]
    connection = connections[context_id]

    if connection["first_sample_time_stamp"] == None:
        raise Exception("No samples received yet")

    if connection["last_sample_time_stamp"] == None:
        raise Exception("No samples received yet")

    time_difference = connection["last_sample_time_stamp"] - \
        connection["first_sample_time_stamp"]
    time_difference_seconds = time_difference.total_seconds()

    sample_rate = connection["total_samples"] / time_difference_seconds
    print(f"Sample rate: {sample_rate} samples/second")
