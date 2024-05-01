import redis
import configparser
import jsonpickle
from schemas.test_result import TestResult

def setup_redis_connection():
    config = configparser.ConfigParser()

    config.read(r'config/settings/config.ini')

    redis_server_host = config.get("Redis", "redis_server_host")
    redis_server_port = config.get("Redis", "redis_server_port")

    return redis.Redis(host=redis_server_host, port=redis_server_port, decode_responses=True)

def get_and_write_results_to_file_average_time():
    r = setup_redis_connection()

    all_keys = r.keys()

    #filename = "overall_results.txt"

    with open(filename, "w") as file:
        file.write("AVERAGE TIME CALCULATIONS:\n\n")
        for key in all_keys:
            if "overall" in str(key):
                result_list = r.lrange(key, 0, -1)
                total_time = 0
                count = 0
                run_id = ""
                for result in result_list:
                    res = jsonpickle.decode(result)
                    if count == 0:
                        run_id = res.run_id
                    total_time += res.total_time
                    count += 1
                average_total_time = total_time/len(result_list)
                average_write_time = average_total_time/1000000
                file.write(f"Run ID: {run_id}\nTotal Time: {average_total_time}\nAverage Time: {average_write_time}\nPossible Writes Per Second: {1/average_write_time}\nAmount of Pods: {len(result_list)}\n\n")
        file.write("--------------------\n\n")

def get_and_write_results_to_file_max_time():
    r = setup_redis_connection()

    all_keys = r.keys()

    #filename = "overall_results_proxy.txt"

    with open(filename, "a") as file:
        file.write("MAX TIME CALCULATION:\n\n")
        for key in all_keys:
            if "overall" in str(key):
                result_list = r.lrange(key, 0, -1)
                total_time = 0
                count = 0
                run_id = ""
                for result in result_list:
                    res = jsonpickle.decode(result)
                    if count == 0:
                        run_id = res.run_id
                    if res.total_time > total_time:
                        total_time = res.total_time
                    count += 1
                average_write_time = total_time/1000000
                file.write(f"Run ID: {run_id}\nTotal Time: {total_time}\nAverage Time: {average_write_time}\nPossible Writes Per Second: {1/average_write_time}\nAmount of Pods: {len(result_list)}\n\n")

if __name__ == '__main__':
    filename = "overall_results_piggy_bouncer.txt"
    get_and_write_results_to_file_average_time()
    get_and_write_results_to_file_max_time()