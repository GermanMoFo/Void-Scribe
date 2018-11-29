import queue
import firebase_admin.firestore
import FireStore_Uploader
import Utilities

_RequestsQueue_ = queue.Queue()
def EnqueueRequest(request_document):
    _RequestsQueue_.put(request_document)

def __ProcessNameRequest__(request_document):
    import NameGenerator
    
    values = request_document.to_dict()
    name_type, amount = values["Req_Arguments"]["Name_Type"], values["Req_Arguments"]["Amount"]
    gen_names = NameGenerator.MarkovName(Name_Type=name_type, amount=amount)
    return gen_names




_AlgorithmRequestMap_ = {"Name":__ProcessNameRequest__}
__StorageCollectionMap__ = {"Name":FireStore_Uploader.DataBaseReference.collection("Generated_Names")}


def __ProcessRequest__(request_document):
    values = request_document.to_dict()
    req_type = values["Req_Type"]

    processed_req = _AlgorithmRequestMap_[req_type](request_document)

    #Format Completed_Request and Storage documents then send them for uploading
    proc_req_doc = {}
    proc_req_doc["Request"] = values
    proc_req_doc["Processed_Request"] = processed_req
    proc_req_doc["Timestamp"] = Utilities.GetTimeStamp()
    proc_req_doc["User_ID"] = values["User_ID"]

    storage_doc = {}
    storage_doc["User_ID"] = values["User_ID"]
    storage_doc["Data"] = processed_req
    storage_doc["Timestamp"] = Utilities.GetTimeStamp()

    
    proc_doc_colec_ref = FireStore_Uploader.DataBaseReference.collection("Completed_Requests")
    storage_doc_colec_ref = __StorageCollectionMap__[values["Req_Type"]]

    FireStore_Uploader.EnqueueDocument(proc_doc_colec_ref, proc_req_doc)
    FireStore_Uploader.EnqueueDocument(storage_doc_colec_ref, storage_doc)

def AlgorithmProcessorEntryPoint():
    
    shut_down = False
    def Shutdown_Processor():
        nonlocal shut_down
        shut_down = True
    from Main import AddShutDownProcess
    AddShutDownProcess(Shutdown_Processor)

    while True:
        if shut_down:
            break
        
        alg_req = None
        try:
            alg_req = _RequestsQueue_.get(timeout=1/10)
        except:
            continue

        if alg_req == None:
            continue
        
        __ProcessRequest__(alg_req)

        

        





# import NameGenerator
# print(NameGenerator.MarkovName(Name_Type="pokemon", amount=50))


    

