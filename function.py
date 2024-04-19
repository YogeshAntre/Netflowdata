from incoming_function import incoming_func
from outgoing_func import outgoing_func
from utilities.crud import *
from incoming_functionwith_subnet import*
from out_with_subnet import *
from incoming_func_with_all_subnet import *
from outgoing_func_with_all_subnet import *
from top_app_outgoing import *
from top_app_incoming import *
from conf.logger_config import logger

def allDevices():
    query = {"size": 0, "query": {"match_all": {}}, "aggs": {
        "unique_values": {"terms": {"field": "devname.keyword"}}}}
    response = get_by_query_agg(index_name='abg_processed', query=query)
    if not response:
        #return {"status": False, "msg": "No data found"}
        return []
    response = [res['key']
                    for res in response['aggregations']['unique_values']['buckets']]
    return response
def getallreport(data):
    device = data['devname']

    query = {"size":0,"query":{"bool":{"must":[{"match":{"devname.keyword":device}},{"bool":{"must":[{"match":{"dstintfrole.keyword":"wan"}}]}}]}},"aggs":{"unique_dstintf":{"terms":{"field":"dstintf.keyword"}}}}
    response = get_by_query_agg(index_name='abg_processed_update', query=query)
    if not response:
        return []
    response = [res['key']
                for res in response['aggregations']['unique_dstintf']['buckets']]
    interface_query = {"size":0,"query":{"bool":{"must":[{"match":{"devname.keyword":device}},{"bool":{"should":[{"match":{"srcintfrole.keyword":"wan"}}]}}]}},"aggs":{"unique_srcintf":{"terms":{"field":"srcintf.keyword"}}}}
    response1 = get_by_query_agg(index_name='abg_processed_update', query=interface_query)
    if not response:
        return []
    response1 = [res['key']
                for res in response1['aggregations']['unique_srcintf']['buckets']]
    response.extend(response1)
    return set(response)


def getalltableAndGraph(data):
    gte = data["gte"]
    lte = data["lte"]
    device = data["devname"]
    direction = data["direction"]
    interface = data["interface"]
    
    if gte > lte:
        return {
            "status": False,
            "msg": " LTE must be greator than GTE",
        }
    try:
        if direction.lower()=="incoming":
             
            data=incoming_func_app(gte,lte,device,interface)
            return data
            
        if direction.lower()=="outgoing":
            data=outgoing_func_app(gte,lte,device,interface)
            return data
            
    except Exception as e:
        logger.exception(f"exception in getalltableAndGraphFunction: {str(e)}")
        return e
def getFinalData(data):
    if data.get('subnet')!=[]:
        return getalltableAndGraphdataAllSubnet(data)
    return getalltableAndGraphdata(data)

def getalltableAndGraphdataAllSubnet(data):
    gte = data["gte"]
    lte = data["lte"]
    device = data["devname"]
    direction = data["direction"]
    interface = data["interface"]
    reportType=data["reportType"]
    subnets=data["subnet"]
    
    if gte > lte:
        return {
            "status": False,
            "msg": " LTE must be greator than GTE",
        }
    if reportType.lower() == "top source":
             report = "srcip.keyword"
    elif reportType.lower() == "top destination":
             report = "dstip.keyword"
    try:
        if direction.lower()=="incoming":
            data=incoming_func_with_subnet_all(gte,lte,device,interface,report,subnets)
            return data
            
        if direction.lower()=="outgoing":
            data=outgoing_func_with_subnet_all(gte,lte,device,interface,report,subnets)
            return data
            
    except Exception as e:
        logger.exception(f"exception in getalltableAndGraphdataAllSubnetFunction: {str(e)}")
        return e



def getalltableAndGraphdataSubnet(data:dict,subnet_data:str,subnet_mask:str):
    gte = data["gte"]
    lte = data["lte"]
    device = data["devname"]
    direction = data["direction"]
    interface = data["interface"]
    reportType=data["reportType"]
    subnet=data["subnet"]
    # gte= data.get("gte"),
    # lte=data.get("lte"),
    # device=data.get("devname"),
    # interface=data.get("interface"),
    # reportType= data.get("reportType"),
    # direction=data.get("direction")
    if subnet_data is None and subnet_mask is None:
        # Both subnet_data and subnet_mask are None, use the value from data["subnet"]
        subnet_data, subnet_mask = data["subnet"].split("/")
    subnet=f"{subnet_data}/{subnet_mask}"
    #return subnet
    data_dict=dict(gte=gte,lte=lte,devname=device,interface=interface,reportType=reportType,direction=direction,subnet=subnet)
    #print(data_dict)
    #return data_dict
    if gte > lte:
        return {
            "status": False,
            "msg": " LTE must be greator than GTE",
        }
    if reportType.lower() == "top source":
             report = "srcip.keyword"
    elif reportType.lower() == "top destination":
             report = "dstip.keyword"
    try:
        if direction.lower()=="incoming":
            data=incoming_func_with_subnet(gte,lte,device,interface,report,subnet)
            return data
          
        if direction.lower()=="outgoing":
            data=outgoing_func_with_subnet(gte,lte,device,interface,report,subnet)
            return data
            
    except Exception as e:
        logger.exception(f"exception in getalltableAndGraphdataSubnetFunction: {str(e)}")
        return e


    
def getalltableAndGraphdata(data):
    gte = data["gte"]
    lte = data["lte"]
    device = data["devname"]
    direction = data["direction"]
    interface = data["interface"]
    reportType=data["reportType"]
    
    if gte > lte:
        return {
            "status": False,
            "msg": " LTE must be greator than GTE",
        }

    try : 

        if reportType.lower() == "top source":
             report = "srcip.keyword"
        elif reportType.lower() == "top destination":
             report = "dstip.keyword"
        # graph_list_values_src=[]
        # graph_list_values_dst=[]
        if direction.lower()=="incoming":
            #print('IN')
            # graph_query ={"size":0,"query":{"bool":{"must":[{"range":{"time_stamp":{"gte":gte,"lte":lte}}},{"match":{"devname.keyword":device}}]}},"aggs":{"src_filters":{"filter":{"bool":{"must":[{"match":{"srcintfrole.keyword":"wan"}},{"match":{"srcintf.keyword":interface}}]}},"aggs":{"incoming_dir_src_ip":{"terms":{"field":report},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min":gte,"max":  lte}},"aggs":{"sent_byte_sum":{"sum":{"field":"rcvd_byte"}}}}}}}},"dst_filters":{"filter":{"bool":{"must":[{"match":{"dstintfrole.keyword":"wan"}},{"match":{"dstintf.keyword":interface}}]}},"aggs":{"incoming_dir_dst_ip":{"terms":{"field":report},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {
            # "min": gte,"max":  lte}} ,"aggs":{"rcvd_byte_sum":{"sum":{"field":"sent_byte"}}}}}}}}}}
            #print('query',graph_query)
            respo = incoming_func(lte,gte,device,interface,report)
            #print('__________________________________')
            return respo
        if direction.lower()=="outgoing":
            #print('Out')
            respo = outgoing_func(lte,gte,device,interface,report)

            return respo
            # graph_query={"size":0,"query":{"bool":{"must":[{"match":{"devname.keyword":device}}]}},"aggs":{"outgoing_dir_src_filters":{"filter":{"bool":{"must":[{"match":{"srcintfrole.keyword":"wan"}},{"match":{"srcintf.keyword":interface}}]}},"aggs":{"incoming_dir_src_ip":{"terms":{"field":report},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min": gte,"max":  lte}},"aggs":{"sent_byte_sum":{"sum":{"field":"sent_byte"}}}}}}}},"dst_filters":{"filter":{"bool":{"must":[{"match":{"dstintfrole.keyword":"wan"}},{"match":{"dstintf.keyword":interface}}]}},"aggs":{"outgoing_dir_dst_ip":{"terms":{"field":report},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min": gte,"max":  lte}},"aggs":{"rcvd_byte_sum":{"sum":{"field":"rcvd_byte"}}}}}}}}}}    
        
        # graph_resp = get_by_query_agg(index_name = "abg_processed_update", query = graph_query)
        # #print('graph_resp',graph_resp)
        # #return graph_resp
        
        # if not graph_resp:
        #         return []

        # graph_respons_dst = [res for res in graph_resp["aggregations"]["dst_filters"]["incoming_dir_dst_ip"]["buckets"]]
        # #print("graph_respons_dst",graph_respons_dst)
        # graph_respons_src = [res for res in graph_resp["aggregations"]["src_filters"]["incoming_dir_src_ip"]["buckets"]]
        # #print("graph_respons_src",graph_respons_src)
        # #print(graph_respons)
        # for graph in graph_respons_src:
        #         graph_data_src_values = []
        #         for date in graph.get('5_min_sum_buckets').get('buckets'):
        #             graph_data_src = []

        #             graph_data_src.append(date["key_as_string"][:-8] )
        #             graph_data_src.append(round((date["sent_byte_sum"]["value"]*8/300),2))
        #             graph_data_src_values.append(graph_data_src)
        #         graph_dict = {
        #                         "appname": graph.get("key"),
        #                         "data": graph_data_src_values
        #                     }            
        #         graph_list_values_src.append(graph_dict)
        # for graph in graph_respons_dst:
        #         graph_data_values_dst = []
        #         for date in graph.get('5_min_sum_buckets').get('buckets'):
        #             graph_data_dst = []

        #             graph_data_dst.append(date["key_as_string"][:-8] )
        #             graph_data_dst.append(round((date["rcvd_byte_sum"]["value"]*8/300),2))
        #             graph_data_values_dst.append(graph_data_dst)
        #         graph_dict = {
        #                         "appname": graph.get("key"),
        #                         "data": graph_data_values_dst
        #                     }            
        #         graph_list_values_dst.append(graph_dict)
        # print(graph_list_values_dst)
        # print("***************************")
        # print(graph_list_values_src)
        # from collections import defaultdict

        # def merge_lists(graph_list_values_dst, graph_list_values_src):
        #     merged_data = defaultdict(list)
        #     for item in graph_list_values_dst + graph_list_values_src:
        #         appname = item['appname']
        #         data = item['data']
        #         for timestamp, value in data:
        #             found = False
        #             for existing_data in merged_data[appname]:
        #                 if existing_data[0] == timestamp:
        #                     existing_data[1] += value
        #                     found = True
        #                     break
        #             if not found:
        #                 merged_data[appname].append([timestamp, value])
        #     result = [{'appname': appname, 'data': data} for appname, data in merged_data.items()]
        #     return result
        #     #print('Merged Data', result)
        # final_graph_list_values=merge_lists(graph_list_values_dst, graph_list_values_src)
        # #return graph_list_values_src
        # result = {}
        # for item in final_graph_list_values:
        #     appname = item.get("appname")
        #     values = [x[1] for x in item["data"]]
        #     total = round(sum(values),2)
        #     minimum = round(min(values),2)
        #     maximum = round(max(values),2)
        #     average = round(total / len(values),2)
        #     result[appname] = {

        #         "sum": round(total,2),
        #         "min": round(minimum,2),
        #         "max": round(maximum,2),
        #         "avg": round(average,2),
        #     }
        # sorted_metrics = sorted(result.items(), key=lambda x: x[1]["avg"], reverse=True)
        # top_10_apps_list = []
        # for metric_name, metric_data in sorted_metrics:
        #     if len(top_10_apps_list) <10:
        #         data = {
        #             'appname': metric_name ,
        #             'sum' : round(metric_data["sum"],2),
        #             'min' : round(metric_data["min"],2),
        #             'max' : round(metric_data["max"],2) ,
        #             'avg' : round(metric_data["avg"],2) ,
        #         }
        #         top_10_apps_list.append(data)
        # top_10_apps_name =[ ]
        # for app_name in top_10_apps_list:
        #     top_10_apps_name.append(app_name.get("appname"))
        # top_10_graph_list = []
        # others_graph_list = []
        # for graph in final_graph_list_values: 
        #     if  graph.get("appname") not in top_10_apps_name : 
        #         others_graph_list.append(graph)     
        #     else:
               
        #         top_10_graph_list.append(graph)
        # data_dict = {app.get("appname"): app for app in top_10_graph_list}

        # top_10_graph_list1 = [data_dict[app_name] for app_name in top_10_apps_name]
        
        # time_interval_totals = {}
        # for app_entry in others_graph_list:
        #     for timestamp, byte_count in app_entry['data']:
        #         if timestamp in time_interval_totals:
        #             time_interval_totals[timestamp] += byte_count
        #         else:
        #             time_interval_totals[timestamp] = byte_count

        # others_list = []
        # time_ = []
        # for k,v in time_interval_totals.items():
        #     others = []
        #     others.append(k)
        #     others.append(round(v,2))
        #     time_.append(v)
        #     others_list.append(others)
        # if time_ :
        #     total_sum = round(sum(time_),2)
        #     min_value = round(min(time_),2)
        #     max_value = round(max(time_),2)
        #     average = round(sum(time_) / len(time_),2)
        #     output = {
        #         "appname": "Others",
        #         "sum": round(total_sum,2),
        #         "min": round(min_value,2),
        #         "max": round(max_value,2),
        #         "avg": round(average,2),
        #     }
        #     top_10_apps_list.append(output)
        # if others_list :
        #     graph_dict1 = {
        #             'appname': "others" ,
        #             "data": others_list
        #         }
        #     top_10_graph_list1.append(graph_dict1)
        # return dict(list_values = top_10_apps_list, graph_list_values  = top_10_graph_list1)
    except Exception as e:
        logger.exception(f"exception in getalltableAndGraphdataFunction: {str(e)}")
        return e
    





