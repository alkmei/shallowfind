import { NestFactory } from '@nestjs/core';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from '../src/app.module';
import * as fs from 'fs';

async function generateOpenAPISpec() {
  const app = await NestFactory.create(AppModule);

  const config = new DocumentBuilder()
    .setTitle('Shallowfind')
    .setDescription('Shallowfind Lifetime Financial Planner API')
    .setVersion('0.0.1a')
    .addTag('api')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);

  // Save as JSON
  fs.writeFileSync('./openapi.json', JSON.stringify(document, null, 2));

  console.log('OpenAPI specification generated successfully!');
  await app.close();
}

void generateOpenAPISpec();
