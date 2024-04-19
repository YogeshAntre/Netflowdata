from utilities.crud import*
from subnet import *
import json
import pandas as pd
def outgoing_func_with_subnet_all(gte,lte,device,interface,report,subnets):

        top_10_graph_list1=[]
        sub_all_sums=[]
        for subnet in subnets:
            #print('********All Subnet*********')
            #print(subnet)
            graph_list_values_src=[]
            graph_list_values_dst=[]
            graph_query={"size":0,"query":{"bool":{"must":[{"range":{"time_stamp":{"gte":gte,"lte":lte}}},{"match":{"devname.keyword":device}}]}},"aggs":{"outgoing_dir_src_filters":{"filter":{"bool":{"must":[{"match":{"srcintfrole.keyword":"wan"}},{"match":{"srcintf.keyword":interface}}]}},"aggs":{"outgoing_dir_src_ip":{"terms":{"field":report,"size":10000},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min": gte,"max":  lte}},"aggs":{"sent_byte_sum":{"sum":{"field":"sent_byte"}}}}}}}},"dst_filters":{"filter":{"bool":{"must":[{"match":{"dstintfrole.keyword":"wan"}},{"match":{"dstintf.keyword":interface}}]}},"aggs":{"outgoing_dir_dst_ip":{"terms":{"field":report,"size":10000},"aggs":{"5_min_sum_buckets":{"date_histogram":{"field":"time_stamp","fixed_interval":"5m","extended_bounds": {"min": gte,"max":  lte}},"aggs":{"rcvd_byte_sum":{"sum":{"field":"rcvd_byte"}}}}}}}}}}

           
            graph_resp = get_by_query_agg(index_name = "abg_processed_new_ips", query = graph_query)
            #print('graph_resp',graph_resp)
            #return graph_resp
             
            if not graph_resp:
                []

            graph_respons_dst = [res for res in graph_resp["aggregations"]["outgoing_dir_src_filters"]["outgoing_dir_src_ip"]["buckets"]]
            #print("graph_respons_dst",graph_respons_dst)
            graph_respons_src = [res for res in graph_resp["aggregations"]["dst_filters"]["outgoing_dir_dst_ip"]["buckets"]]
            #print("graph_respons_src",graph_respons_src)
            #print(graph_respons)
            for graph in graph_respons_src:
                    graph_data_src_values = []
                    for date in graph.get('5_min_sum_buckets').get('buckets'):
                        graph_data_src = []

                        graph_data_src.append(date["key_as_string"][:-8] )
                        graph_data_src.append(round((date["rcvd_byte_sum"]["value"]*8/300),2))
                        graph_data_src_values.append(graph_data_src)
                    graph_dict = {
                                    "appname": graph.get("key"),
                                    "data": graph_data_src_values
                                }            
                    graph_list_values_src.append(graph_dict)
            for graph in graph_respons_dst:
                    graph_data_values_dst = []
                    for date in graph.get('5_min_sum_buckets').get('buckets'):
                        graph_data_dst = []

                        graph_data_dst.append(date["key_as_string"][:-8] )
                        graph_data_dst.append(round((date["sent_byte_sum"]["value"]*8/300),2))
                        graph_data_values_dst.append(graph_data_dst)
                    graph_dict = {
                                    "appname": graph.get("key"),
                                    "data": graph_data_values_dst
                                }            
                    graph_list_values_dst.append(graph_dict)
            #return graph_list_values_dst
            #print("***************************")
            #print(graph_list_values_src)
            from collections import defaultdict

            def merge_lists(graph_list_values_dst, graph_list_values_src):
                merged_data = defaultdict(list)
                for item in graph_list_values_dst + graph_list_values_src:
                    appname = item['appname']
                    data = item['data']
                    for timestamp, value in data:
                        found = False
                        for existing_data in merged_data[appname]:
                            if existing_data[0] == timestamp:
                                existing_data[1] += value
                                found = True
                                break
                        if not found:
                            merged_data[appname].append([timestamp, value])
                result = [{'appname': appname, 'data': data} for appname, data in merged_data.items()]
                
                #print('Merged Data', result)
                return result
            final_graph_list_values=merge_lists(graph_list_values_dst, graph_list_values_src)
             
            ip_sub=generate_ips(subnet)
            #print(ip_sub)
            filtered_data = [item for item in final_graph_list_values if item["appname"] in ip_sub]
            if not filtered_data:
                continue
            #return filtered_data
            #return graph_list_values_src
           # return final_graph_list_values
            
            time_interval_totals = {}
            for app_entry in filtered_data:
                        # # return app_entry
                        # for apps in app_entry :
                        #     return apps
                        for timestamp, byte_count in app_entry['data']:
                            if timestamp in time_interval_totals:
                                time_interval_totals[timestamp] += byte_count
                            else:
                                time_interval_totals[timestamp] = byte_count
            others_list = []
            for k,v in time_interval_totals.items():
                        others = []
                        others.append(k)
                        others.append(round(v,2))
                        others_list.append(others)
                    
                    
            graph_dict1 = {
                        'appname': subnet ,
                        "data": others_list
                    }
            top_10_graph_list1.append(graph_dict1)
                    #all_ip_list.append(graph_list_values)
            result = {}
            for item in filtered_data:
                        appname = item.get("appname")
                        values = [x[1] for x in item["data"]]
                        # print('values',values)
                        total = round(sum(values),2)
                        minimum = round(min(values),2)
                        maximum = round(max(values),2)
                        average = round(total / len(values),2)
                        result[appname] = {
                            "sum": round(total,2),
                            "min": round(minimum,2),
                            "max": round(maximum,2),
                            "avg": round(average,2),
                        }
                        #print('Result',result)
                #return result
            sum_values = [values['sum'] for values in result.values()]
                #print(sum_values)
            min_values = [values['min'] for values in result.values()]
            max_values = [values['max'] for values in result.values()]
                    #print('data',len(sum_values))
                    # total_length=len(values)
            total_sum=sum(sum_values)
            total_min= min(min_values)
            total_max= max(max_values)
            average= (total_sum / len(values))
            list_values=[]
            sub_all_sums.append({
                            'appname' : subnet,
                            "sum": round(total_sum,2),
                            "min": round(total_min,2),
                            "max": round(total_max,2),
                            "avg": round(average,2)
                    })
            #print(sub_all_sums)
            # data=dict(list_values=sub_all_sums)
            # df = pd.DataFrame(data)
            # df.to_excel('top_source_outgoing_10_17_47_13.xlsx', index=False)
        return dict(list_values=sub_all_sums,graph_list_values=top_10_graph_list1)
