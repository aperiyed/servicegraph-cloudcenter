import logging
import requests
from servicegraph.firewall.asav import ASA

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)


class SGManager:

    def __init__(self, apic_ip, apic_username, apic_password, cliqr_provider_tier_name, cliqr_consumer_tier_name,
                 env_map):
        self.apic_ip = apic_ip
        self.apic_username = apic_username
        self.apic_password = apic_password
        self.env_map = env_map
        self.cliqr_provider_tier_name = cliqr_provider_tier_name  # from env file value -- "cliqrAppTierName": "Db"
        self.cliqr_consumer_tier_name = cliqr_consumer_tier_name  # from env file value -- "CliqrDependents": "Web"
        self.ipam_url = "http://172.17.152.185:5000/ipaddress"

    def __get_nw_details(self):
        consumer_ip_key = "CliqrTier_{0}_IP".format(self.cliqr_consumer_tier_name)
        provider_ip_key = "CliqrTier_{0}_IP".format(self.cliqr_provider_tier_name)
        consumer_ip = self.env_map[consumer_ip_key]
        provider_ip = self.env_map[provider_ip_key]
        consumer_nw_data = self.__get_nw_details_from_ipam(consumer_ip)
        provider_nw_data = self.__get_nw_details_from_ipam(provider_ip)
        return consumer_nw_data, provider_nw_data

    def __get_nw_details_from_ipam(self, ipaddress):
        ipam_query_url = "{0}/{1}".format(self.ipam_url, ipaddress)
        logging.debug(" IPAM Query URL " + ipam_query_url)
        r = requests.get(ipam_query_url)
        r_json = r.json()
        logging.info(" Received NW Details for IP Address " + str(r_json))
        # Response Format --> {"gateway":"172.17.153.1","netmask":"27","network":"172.17.153.0"}
        # Response Format --> {"gateway":"172.17.153.33","netmask":"27","network":"172.17.153.32"}
        r.close()
        return r_json

    def process_service_graph(self):
        env_map_arr = self.env_map["CliqrCloud_AciPortGroup_1"].split("|")
        tenant_name = env_map_arr[0]
        application_profile_name = env_map_arr[1]
        contract_name = "_".join(application_profile_name.split("_")[:-1]) + "_CONTRACT"
        acl_name = "_".join(application_profile_name.split("_")[:-1]) + "_ACL"
        consumer_nw_data, provider_nw_data = self.__get_nw_details()
        asa = ASA.ASA(apic_ip=self.apic_ip, apic_username=self.apic_username, apic_password=self.apic_password,
                      application_profile_name=application_profile_name,
                      consumer_epg_name=self.cliqr_consumer_tier_name + "_1",
                      provider_epg_name=self.cliqr_provider_tier_name + "_1", contract_name=contract_name,
                      tenant_name=tenant_name,
                      servicegraph_template_name="asav69", device_type="asav", acl_name=acl_name,
                      consumer_epg_nw=consumer_nw_data["network"],
                      consumer_epg_nm=consumer_nw_data["netmask"],
                      provider_epg_nw=provider_nw_data["network"], provider_epg_nm=provider_nw_data["netmask"],
                      consumer_interface_ip="172.17.151.5",
                      consumer_interface_gw="172.17.151.1", consumer_interface_nm="29",
                      provider_interface_ip="172.17.151.13",
                      provider_interface_gw="172.17.151.9", provider_interface_nm="29"
                      )
        asa.create_service_graph()

