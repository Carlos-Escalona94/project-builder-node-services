import configure from '@vendia/serverless-express';

import express from 'express';
import cors from 'cors'


let serverlessExpressInstance;

const app = express();

app.use(cors())

// const routes = express.Router({
//     mergeParams: true
// })

app.get('/', (req, res) => {

    console.log("cuack");

    res.status(200).json({
        teste: "este"
    });
})

function asyncTask(){
    return new Promise((resolve) => {
        setTimeout(() => resolve("connected to database"), 1000)
    })
}

async function setup(event, context){
    const asyncValue = await asyncTask();
    console.log(asyncValue);
    serverlessExpressInstance = configure({ app });
    return serverlessExpressInstance(event, context);
}

export const lambdaHandler = (event, context) => {
    if(serverlessExpressInstance) return serverlessExpressInstance(event, context);

    return setup(event, context);
} 