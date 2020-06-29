import re
from app import mongo
from app.util import serialize_doc
from bson.objectid import ObjectId
from app.config import dates_converter

def assign_letter_heads( letterhead_id ):
    letter_head_details = mongo.db.letter_heads.find_one({ "_id": ObjectId(letterhead_id) })
    if letter_head_details is not None:
        header = letter_head_details['header_value']
        footer = letter_head_details['footer_value']
        return { 'header': header, 'footer': footer }
    else:
        return {}

def attach_letter_head( header, footer, message):
    download_pdf = "#letter_head #content #letter_foot"
    if header is not None:
        download_pdf = download_pdf.replace("#letter_head", header)
    else:
        download_pdf = download_pdf.replace("#letter_head", '')
    download_pdf = download_pdf.replace("#content", message)
    if footer is not None:
        download_pdf = download_pdf.replace("#letter_foot", footer)
    else:
        download_pdf = download_pdf.replace("#letter_foot", '')
    return { 'message': download_pdf }


def construct_template( req_message, request ):
    system_variable = mongo.db.mail_variables.find({})
    system_variable = [serialize_doc(doc) for doc in system_variable]
    message_variables = []
    message = req_message.split('#')
    del message[0]
    message_regex = re.compile('!|@|\$|\%|\^|\&|\*|\:')
    for keyword in message:
        message_keyword = re.split(message_regex, keyword)
        message_variables.append(message_keyword[0])
    message_str = req_message
    for detail in message_variables:
        if detail in request:
            if request[detail] is not None:
                rexWithString = '#' + re.escape(detail) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])'
                message_str = re.sub(rexWithString, str(request[detail]), message_str)
        else:
            for element in system_variable:
                if "#" + detail == element['name'] and element['value'] is not None:
                    rexWithSystem = re.escape(element['name']) + r'([!]|[@]|[\$]|[\%]|[\^]|[\&]|[\*]|[\:])' 
                    message_str = re.sub(rexWithSystem, str(element['value']), message_str)    
    missing = message_str.split('#')
    del missing[0]
    missing_payload = convert_response_to_payload(missing=missing)
    
    return { 'message': message_str, 'missing_payload': missing_payload }

#payload going = {"req_message":"message string","request":"data variable","message_detail":"mail template"}
def generate_full_template_from_string_payload(req_message=None, request=None , message_detail=None):
    missing_payload = []
    message_about = construct_template( req_message=req_message, request=request )
    message = message_about.get('message')
    missing_payload.extend(message_about.get('missing_payload'))

    subject_about = construct_template( req_message=req_message, request=request )
    subject = subject_about.get('message')
    missing_payload.extend(subject_about.get('missing_payload'))

    if 'mobile_message' in message_detail:
        mobile_message_about = construct_template( req_message= req_message, request=request )
        mobile_message_str = mobile_message_about.get('message')
        missing_payload.extend(mobile_message_about.get('missing_payload'))

    return missing_payload


def convert_response_to_payload(missing=None):
    missing_payload = []
    missing_regex_value = re.compile('!|@|\$|\%|\^|\&|\*|\:')
    for elem in missing:
        missing_data = re.split(missing_regex_value, elem)
        missing_payload.append({"key": missing_data[0] , "type": "date" if missing_data[0] in dates_converter else "text"})
    return missing_payload