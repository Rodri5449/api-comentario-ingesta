
import boto3
import uuid
import os
import json
import base64

def lambda_handler(event, context):
    # Entrada (JSON)
    print(event)

    # Obtener el contenido recibido
    body = event.get('body', event)

    # Manejar cuando API Gateway envía el body como texto
    if isinstance(body, str):
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')

        body = json.loads(body)

    tenant_id = body['tenant_id']
    texto = body['texto']

    # Obtener nombres de recursos desde las variables de entorno
    nombre_tabla = os.environ['TABLE_NAME']
    nombre_bucket = os.environ['INGEST_BUCKET']

    # Proceso: generar UUID V1
    uuidv1 = str(uuid.uuid1())

    comentario = {
        'tenant_id': tenant_id,
        'uuid': uuidv1,
        'detalle': {
            'texto': texto
        }
    }

    # Guardar comentario en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)
    response = table.put_item(Item=comentario)

    # Convertir comentario a formato JSON
    archivo_json = json.dumps(comentario, ensure_ascii=False)

    # Generar ruta del archivo en S3
    nombre_archivo = f'comentarios/{tenant_id}/{uuidv1}.json'

    # Guardar comentario en el bucket S3 (Ingesta Push)
    s3 = boto3.client('s3')

    s3.put_object(
        Bucket=nombre_bucket,
        Key=nombre_archivo,
        Body=archivo_json.encode('utf-8'),
        ContentType='application/json'
    )

    # Salida
    print(comentario)
    print(f'Comentario almacenado en S3: {nombre_archivo}')

    return {
        'statusCode': 200,
        'comentario': comentario,
        'response': response,
        'archivo_s3': {
            'bucket': nombre_bucket,
            'key': nombre_archivo
        }
    }
