import redis
import configparser
import jsonpickle
from schemas.test_result import TestResult

def setup_redis_connection():
    config = configparser.ConfigParser()

    config.read(r'src/config/settings/config.ini')

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


#Uses the highest total time count to calculate averages and so on
def get_and_write_results_to_file_pools():
    r = setup_redis_connection()

    all_keys = r.keys()

    for key in all_keys:
        if "pools" in str(key):
            if any(key_id in key for key_id in proxy_ids):
                filename = "pool_results_proxy.txt"
                run_id, total_time, average_write_time, list_length = get_results_from_key(key, r)
                amount_of_pods = list_length/4
                write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods)
            elif any(key_id in key for key_id in bouncer_ids):
                filename = "pool_results_bouncer.txt"
                run_id, total_time, average_write_time, list_length = get_results_from_key(key, r)
                amount_of_pods = list_length/4
                write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods)
            elif any(key_id in key for key_id in direct_ids):
                filename = "pool_results_direct.txt"
                run_id, total_time, average_write_time, list_length = get_results_from_key(key, r)
                amount_of_pods = list_length/4
                write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods)
                

#Uses the highest total time count to calculate averages and so on
def get_and_write_results_to_file_overall():
    r = setup_redis_connection()

    all_keys = r.keys()

    for key in all_keys:
        if "overall" in str(key):
            if any(key_id in key for key_id in proxy_ids):
                filename = "overall_results_proxy.txt"
                run_id, total_time, average_write_time, list_length = get_results_from_key(key, r)
                amount_of_pods = list_length
                write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods)
            elif any(key_id in key for key_id in bouncer_ids):
                filename = "overall_results_bouncer.txt"
                run_id, total_time, average_write_time, list_length = get_results_from_key(key, r)
                amount_of_pods = list_length
                write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods)
            elif any(key_id in key for key_id in direct_ids):
                filename = "overall_results_direct.txt"
                run_id, total_time, average_write_time, list_length = get_results_from_key(key, r)
                amount_of_pods = list_length
                write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods)

def write_to_file(filename, run_id, total_time, average_write_time, amount_of_pods):
    with open(filename, "a") as file:
        file.write(f"Run ID: {run_id}\nTotal Time: {total_time}\nAverage Time: {average_write_time}\nPossible Writes Per Second: {1/average_write_time}\nAmount of Pods: {amount_of_pods}\n\n")

def get_results_from_key(key, redis_client):
    result_list = redis_client.lrange(key, 0, -1)
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
    list_length = len(result_list)
    
    return (run_id, total_time, average_write_time, list_length)

if __name__ == '__main__':
    
    proxy_ids = ["fce04686-3f6e-4cfe-a282-e60ccda3a992", "0db13d90-45c0-430b-b306-c3b3eb5a5d1d", "6871ab48-b232-4ef4-8cca-7f5f58291e63"]
    bouncer_ids = ["c16ac1f1-76e8-4ab0-93ff-c145064f6d9e", "0444f7d2-5b65-4ba0-b26a-fcd0dc8cfd77", "48a8b6e1-2fd1-4d1a-bebb-cd4c770c9de9"]
    direct_ids = ["854c22c3-9443-4246-90ed-4bd332552be6", "08cd0ea5-0c91-4a9d-8cd9-a9a805a3a235", "4e90e015-ea93-4461-b458-b73cf2c28a11"]
    
    filename = "overall_results_piggy_bouncer.txt"
    # get_and_write_results_to_file_average_time()
    # get_and_write_results_to_file_max_time()
    
    get_and_write_results_to_file_pools()
    get_and_write_results_to_file_overall()