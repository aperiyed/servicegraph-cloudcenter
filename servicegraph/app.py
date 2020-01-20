import json
import logging

from flask import Flask, request

from servicegraph.SGManager import SGManager

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

app = Flask(__name__)


@app.route('/servicegraph', methods=['POST'])
def process_env_vars():
    logging.info(" Received Request for Service Graph Creation ")
    env_map = request.get_json()
    apic_ip = env_map["CliqrCloud_AciApicEndpoint"].split("//")[1]
    logging.info(" CliqrCloud_AciApicEndpoint -- " + apic_ip)
    apic_username = env_map["CliqrCloud_AciUsername"]
    logging.info(" apic_username -- " + apic_username)
    apic_password = env_map["CliqrCloud_AciPassword"]
    logging.info(" apic_password -- " + apic_password)
    consumer_name = env_map["cliqrAppTierName"]
    logging.info(" consumer_name -- " + consumer_name)
    provider_name = env_map["CliqrDependents"]
    logging.info(" env_map -- " + provider_name)
    logging.info(" Params :: |{0}|{1}|{2}|consumer --> {3}|provider --> {4}|", apic_ip, apic_username, apic_password,
                 consumer_name, provider_name)
    logging.info(" Invoking ServiceGraph Manager ")
    servicegraph_manager = SGManager(apic_ip=apic_ip, apic_username=apic_username, apic_password=apic_password,
                                     cliqr_consumer_tier_name=provider_name, cliqr_provider_tier_name=consumer_name,
                                     env_map=env_map)
    logging.info(" Provisioning ASAv ServiceGraph...")
    servicegraph_manager.process_service_graph()
    logging.info(" ServiceGraph Provisioning Completed!!")
    return "success", 200


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='5001', threaded=True)

