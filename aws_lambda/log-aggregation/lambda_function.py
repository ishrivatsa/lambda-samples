import base64
import gzip
import io
import json
import zlib

## This function will process events/data sent to Kinesis Firehose. These events were aggregated in CloudWatch Logs. CloudWatch logs compresses the logs to reduce the size of data sent. This lambda function will first unzip/uncompress the zipped file. Then it looks for the type of the message/log. In general, there are 2 types of messages: CONTROL_MESSAGE and DATA_MESSAGE. CONTROL_MESSAGE(s) are used for communication between services whereas DATA_MESSAGE(s) are used to store log and event info. In this example, we are dropping the CONTROL_MESSAGE and just forwarding DATA_MESSAGE . 

def lambda_handler(event, context):
    output = []

    for record in event['records']:
      compressed_payload = base64.b64decode(record['data'])
      uncompressed_payload = gzip.decompress(compressed_payload)
      print('uncompressed_payload',uncompressed_payload)
      payload = json.loads(uncompressed_payload)
      
      # Drop messages of type CONTROL_MESSAGE
      if payload.get('messageType') == 'CONTROL_MESSAGE':
          
          output_record = {
              'recordId': record['recordId'],
              'result': 'Dropped'
          }
          return {'records': output}
     
     
       # Do custom processing on the payload here, if needed. 
    
     # Kinesis Firehose expects a particular format for the messages. Make sure the section below is NOT modified. 
      output_record = {
          'recordId': record['recordId'],
          'result': 'Ok',
          'data': base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
      }
      output.append(output_record)

    print('Successfully processed {}        records.'.format(len(event['records'])))

    return {'records': output}
