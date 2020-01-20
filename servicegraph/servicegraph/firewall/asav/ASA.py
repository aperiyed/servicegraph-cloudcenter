import logging
import random

import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.model.vns
import cobra.model.vz
from cobra.internal.codec.xmlcodec import toXMLStr
from cobra.mit.request import ConfigRequest
from cobra.mit.session import LoginSession

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)


class APIC:
    def __init__(self, apic_ip, apic_username, apic_password):
        self.apic_ip = apic_ip
        self.apic_username = apic_username
        self.apic_password = apic_password
        self.apic_url = "https://{0}".format(apic_ip)

    def get_apic_session(self):
        login_session = LoginSession(self.apic_url, self.apic_username, self.apic_password)
        logging.info(" Obtained APIC session object ")
        return login_session


class ASA:
    class Config:
        FW = u'fw'
        NETWORK = u'network'
        NW = u'nw'
        INTERFACE = u'interface'
        IF = u'if'
        EXTERNAL = u'external'
        EXT = u'ext'
        ACL = u'acl'
        ACE = u'ace'
        DESTINATIONIP = u'destinationip'
        DESTINATIONPORT = u'destinationport'
        SOURCEIP = u'sourceip'
        IP = u'ip'
        IPADDRESS = u'ipaddress'
        NM = u'nm'
        NETMASK = u'netmask'

    def __init__(self, apic_ip, apic_username, apic_password, application_profile_name, consumer_epg_name,
                 provider_epg_name,
                 contract_name, tenant_name, servicegraph_template_name, device_type, acl_name, consumer_epg_nw,
                 consumer_epg_nm, provider_epg_nw, provider_epg_nm,
                 consumer_interface_ip, consumer_interface_gw, consumer_interface_nm, provider_interface_ip,
                 provider_interface_gw, provider_interface_nm):
        self.apic_ip = apic_ip
        self.apic_username = apic_username
        self.apic_password = apic_password
        self.application_profile_name = application_profile_name
        self.consumer_epg_name = consumer_epg_name
        self.provider_epg_name = provider_epg_name
        self.contract_name = contract_name
        self.tenant_name = tenant_name
        self.servicegraph_template_name = servicegraph_template_name
        self.device_type = device_type
        self.acl_name = acl_name
        self.apic = APIC(self.apic_ip, self.apic_username, self.apic_password)
        self.ace_name_counter_init = random.randint(1, 1000)
        self.consumer_epg_nw = consumer_epg_nw
        self.consumer_epg_nm = consumer_epg_nm
        self.provider_epg_nm = provider_epg_nm
        self.provider_epg_nw = provider_epg_nw
        self.consumer_interface_ip = consumer_interface_ip
        self.consumer_interface_gw = consumer_interface_gw
        self.consumer_interface_nm = consumer_interface_nm
        self.provider_interface_ip = provider_interface_ip
        self.provider_interface_gw = provider_interface_gw
        self.provider_interface_nm = provider_interface_nm

    # Provider : 172.17.153.9/27
    # Consumer : 172.17.153.37/27
    def __build_service_graph_payload(self):
        logging.info(" Preparing To Build Payload.")
        logging.debug(" Get APIC Session Object ")
        apic_session = self.apic.get_apic_session()
        md = cobra.mit.access.MoDirectory(apic_session)
        md.login()
        topMo = cobra.model.pol.Uni('')
        fvTenant = cobra.model.fv.Tenant(topMo, name=self.tenant_name)
        fvAp = cobra.model.fv.Ap(fvTenant, name=self.application_profile_name)
        fvAEPg = cobra.model.fv.AEPg(fvAp, name=self.consumer_epg_name)
        fvRsCons = cobra.model.fv.RsCons(fvAEPg, tnVzBrCPName=self.contract_name)
        fvAEPg2 = cobra.model.fv.AEPg(fvAp, name=self.provider_epg_name)
        fvRsProv = cobra.model.fv.RsProv(fvAEPg2, tnVzBrCPName=self.contract_name)
        vnsSvcPol = cobra.model.vns.SvcPol(fvAEPg, self.contract_name, self.servicegraph_template_name,
                                           self.device_type)
        vnsFolderInst = cobra.model.vns.FolderInst(vnsSvcPol, graphNameOrLbl=self.servicegraph_template_name,
                                                   ctrctNameOrLbl=self.contract_name,
                                                   key=u'fw', nodeNameOrLbl=self.device_type, name=u'fw')
        vnsFolderInst2 = cobra.model.vns.FolderInst(vnsFolderInst, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'network',
                                                    nodeNameOrLbl=self.device_type,
                                                    name=u'nw')
        vnsFolderInst3 = cobra.model.vns.FolderInst(vnsFolderInst2, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'interface',
                                                    nodeNameOrLbl=self.device_type, name=u'if')
        vnsFolderInst4 = cobra.model.vns.FolderInst(vnsFolderInst3, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'external',
                                                    nodeNameOrLbl=self.device_type,
                                                    name=u'ext')
        vnsFolderInst5 = cobra.model.vns.FolderInst(vnsFolderInst4, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'acl',
                                                    nodeNameOrLbl=self.device_type,
                                                    name=self.acl_name)
        vnsFolderInst6 = cobra.model.vns.FolderInst(vnsFolderInst5, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'ace',
                                                    nodeNameOrLbl=self.device_type,
                                                    name=u'ace_10')
        vnsFolderInst7 = cobra.model.vns.FolderInst(vnsFolderInst6, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'destinationip',
                                                    nodeNameOrLbl=self.device_type,
                                                    name=u'ace_destinationip_' + self.consumer_epg_nw)
        vnsParamInst = cobra.model.vns.ParamInst(vnsFolderInst7, name=u'ip', value=self.consumer_epg_nw,
                                                 key=u'ipaddress')
        vnsParamInst2 = cobra.model.vns.ParamInst(vnsFolderInst7, name=u'nm', value=self.consumer_epg_nm,
                                                  key=u'netmask')
        vnsFolderInst8 = cobra.model.vns.FolderInst(vnsFolderInst6, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'destinationport',
                                                    nodeNameOrLbl=self.device_type, name=u'ace_destinationport_8888')
        vnsParamInst3 = cobra.model.vns.ParamInst(vnsFolderInst8, name=u'pt', value=u'8888', key=u'port')
        vnsFolderInst9 = cobra.model.vns.FolderInst(vnsFolderInst6, graphNameOrLbl=self.servicegraph_template_name,
                                                    ctrctNameOrLbl=self.contract_name, key=u'protocol',
                                                    nodeNameOrLbl=self.device_type,
                                                    name=u'ace_protocol_TCP')
        vnsParamInst4 = cobra.model.vns.ParamInst(vnsFolderInst9, name=u'pro', value=u'TCP', key=u'protocol')
        vnsFolderInst10 = cobra.model.vns.FolderInst(vnsFolderInst6, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'sourceip',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'ace_sourceip_' + self.provider_epg_nw)
        vnsParamInst5 = cobra.model.vns.ParamInst(vnsFolderInst10, name=u'ip', value=self.provider_epg_nw,
                                                  key=u'ipaddress')
        vnsParamInst6 = cobra.model.vns.ParamInst(vnsFolderInst10, name=u'nm', value=self.provider_epg_nm,
                                                  key=u'netmask')
        vnsParamInst7 = cobra.model.vns.ParamInst(vnsFolderInst6, name=u'act', value=u'PERMIT', key=u'action')
        vnsParamInst8 = cobra.model.vns.ParamInst(vnsFolderInst6, name=u'ord', value=u'10', key=u'order')
        vnsFolderInst11 = cobra.model.vns.FolderInst(vnsFolderInst5, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'ace',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'ace_11')
        vnsFolderInst12 = cobra.model.vns.FolderInst(vnsFolderInst11, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'destinationip',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'ace_destinationip_' + self.consumer_epg_nw)
        vnsParamInst9 = cobra.model.vns.ParamInst(vnsFolderInst12, name=u'ip', value=self.consumer_epg_nw,
                                                  key=u'ipaddress')
        vnsParamInst10 = cobra.model.vns.ParamInst(vnsFolderInst12, name=u'nm', value=self.consumer_epg_nm,
                                                   key=u'netmask')
        vnsFolderInst13 = cobra.model.vns.FolderInst(vnsFolderInst11, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'protocol',
                                                     nodeNameOrLbl=self.device_type, name=u'ace_protocol_ICMP')
        vnsParamInst11 = cobra.model.vns.ParamInst(vnsFolderInst13, name=u'pro', value=u'ICMP', key=u'protocol')
        vnsFolderInst14 = cobra.model.vns.FolderInst(vnsFolderInst11, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'sourceip',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'ace_sourceip_' + self.provider_epg_nw)
        vnsParamInst12 = cobra.model.vns.ParamInst(vnsFolderInst14, name=u'ip', value=self.provider_epg_nw,
                                                   key=u'ipaddress')
        vnsParamInst13 = cobra.model.vns.ParamInst(vnsFolderInst14, name=u'nm', value=self.provider_epg_nm,
                                                   key=u'netmask')
        vnsParamInst14 = cobra.model.vns.ParamInst(vnsFolderInst11, name=u'act', value=u'PERMIT', key=u'action')
        vnsParamInst15 = cobra.model.vns.ParamInst(vnsFolderInst11, name=u'ord', value=u'11', key=u'order')
        vnsFolderInst15 = cobra.model.vns.FolderInst(vnsFolderInst4, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'ip',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'ip_' + self.consumer_interface_ip)
        vnsParamInst16 = cobra.model.vns.ParamInst(vnsFolderInst15, name=u'ip', value=self.consumer_interface_ip,
                                                   key=u'ipaddress')
        vnsParamInst17 = cobra.model.vns.ParamInst(vnsFolderInst15, name=u'nm', value=self.consumer_interface_nm,
                                                   key=u'netmask')
        vnsFolderInst16 = cobra.model.vns.FolderInst(vnsFolderInst4, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'route',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'rt_' + self.consumer_interface_gw + '_' + self.provider_epg_nw + '_' + self.provider_epg_nm)
        vnsParamInst18 = cobra.model.vns.ParamInst(vnsFolderInst16, name=u'gw', value=self.consumer_interface_gw,
                                                   key=u'gateway')
        vnsParamInst19 = cobra.model.vns.ParamInst(vnsFolderInst16, name=u'ip', value=self.provider_epg_nw,
                                                   key=u'ipaddress')
        vnsParamInst20 = cobra.model.vns.ParamInst(vnsFolderInst16, name=u'nm', value=self.provider_epg_nm,
                                                   key=u'netmask')
        vnsFolderInst17 = cobra.model.vns.FolderInst(vnsFolderInst3, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'internal',
                                                     nodeNameOrLbl=self.device_type, name=u'int')
        vnsFolderInst18 = cobra.model.vns.FolderInst(vnsFolderInst17, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'ip',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=self.provider_interface_ip)
        vnsParamInst21 = cobra.model.vns.ParamInst(vnsFolderInst18, name=u'ip', value=self.provider_interface_ip,
                                                   key=u'ipaddress')
        vnsParamInst22 = cobra.model.vns.ParamInst(vnsFolderInst18, name=u'nm', value=self.provider_interface_nm,
                                                   key=u'netmask')
        vnsFolderInst19 = cobra.model.vns.FolderInst(vnsFolderInst17, graphNameOrLbl=self.servicegraph_template_name,
                                                     ctrctNameOrLbl=self.contract_name, key=u'route',
                                                     nodeNameOrLbl=self.device_type,
                                                     name=u'rt_' + self.provider_interface_gw + '_' + self.consumer_epg_nw + '_' + self.consumer_epg_nm)
        vnsParamInst23 = cobra.model.vns.ParamInst(vnsFolderInst19, name=u'gw', value=self.provider_interface_gw,
                                                   key=u'gateway')
        vnsParamInst24 = cobra.model.vns.ParamInst(vnsFolderInst19, name=u'ip', value=self.consumer_epg_nw,
                                                   key=u'ipaddress')
        vnsParamInst25 = cobra.model.vns.ParamInst(vnsFolderInst19, name=u'nm', value=self.consumer_epg_nm,
                                                   key=u'netmask')
        vnsRsFolderInstToMFolder = cobra.model.vns.RsFolderInstToMFolder(vnsFolderInst,
                                                                         tDn=u'uni/infra/mDev-CISCO-CloudMode-1.0/mFunc-FW/mFolder-fw')
        vzBrCP = cobra.model.vz.BrCP(fvTenant, name=self.contract_name)
        vzSubj = cobra.model.vz.Subj(vzBrCP, name=u'Subject')
        vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, tnVzFilterName=u'default')
        vzRsSubjGraphAtt = cobra.model.vz.RsSubjGraphAtt(vzSubj, tnVnsAbsGraphName=self.servicegraph_template_name)
        vnsLDevCtx = cobra.model.vns.LDevCtx(fvTenant, ctrctNameOrLbl=self.contract_name,
                                             graphNameOrLbl=self.servicegraph_template_name,
                                             nodeNameOrLbl=self.device_type)
        vnsLIfCtx = cobra.model.vns.LIfCtx(vnsLDevCtx, connNameOrLbl=u'consumer')
        vnsRsLIfCtxToBD = cobra.model.vns.RsLIfCtxToBD(vnsLIfCtx, tDn=u'uni/tn-VEL_DEV/BD-asav-external')
        vnsRsLIfCtxToLIf = cobra.model.vns.RsLIfCtxToLIf(vnsLIfCtx, tDn=u'uni/tn-VEL_DEV/lDevVip-asav69/lIf-External')
        vnsRsLIfCtxToSvcRedirectPol = cobra.model.vns.RsLIfCtxToSvcRedirectPol(vnsLIfCtx,
                                                                               tDn=u'uni/tn-VEL_DEV/svcCont/svcRedirectPol-External')
        vnsLIfCtx2 = cobra.model.vns.LIfCtx(vnsLDevCtx, connNameOrLbl=u'provider')
        vnsRsLIfCtxToBD2 = cobra.model.vns.RsLIfCtxToBD(vnsLIfCtx2, tDn=u'uni/tn-VEL_DEV/BD-asav-internal')
        vnsRsLIfCtxToLIf2 = cobra.model.vns.RsLIfCtxToLIf(vnsLIfCtx2, tDn=u'uni/tn-VEL_DEV/lDevVip-asav69/lIf-Internal')
        vnsRsLIfCtxToSvcRedirectPol2 = cobra.model.vns.RsLIfCtxToSvcRedirectPol(vnsLIfCtx2,
                                                                                tDn=u'uni/tn-VEL_DEV/svcCont/svcRedirectPol-Internal')
        vnsRsLDevCtxToLDev = cobra.model.vns.RsLDevCtxToLDev(vnsLDevCtx, tDn=u'uni/tn-VEL_DEV/lDevVip-asav69')

        # commit the generated code to APIC
        logging.debug(" Generated XML Payload ")
        print toXMLStr(topMo)
        return topMo, md

    def create_service_graph(self):
        logging.info(" Preparing To Create Service Graph.")
        topMo, md = self.__build_service_graph_payload()
        config_request = ConfigRequest()
        config_request.addMo(topMo)
        md.commit(config_request)

