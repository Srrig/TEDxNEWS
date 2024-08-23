export const handler = async (event) => {
    // TODO implement
    const response = {
      statusCode: 200,
      headers: {
                  'Access-Control-Allow-Origin': '*', // Permette l'accesso da qualsiasi origine
                  'Access-Control-Allow-Methods': 'OPTIONS,POST,GET', // Metodi consentiti
                  'Access-Control-Allow-Headers': 'Content-Type', // Header consentiti
              },
              body: JSON.stringify('CORS preflight success'),
    };
    return response;
  };
  