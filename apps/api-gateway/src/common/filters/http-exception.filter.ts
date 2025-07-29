import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Response } from 'express';
import { ApiResponse } from '../interfaces/api-response.interface';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    let status = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Internal server error';
    let error: any = null;

    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === 'string') {
        message = exceptionResponse;
      } else if (
        typeof exceptionResponse === 'object' &&
        exceptionResponse !== null
      ) {
        message =
          (exceptionResponse as { message: string }).message ||
          exception.message;
        error = exceptionResponse;
      }
    } else if (exception instanceof Error) {
      message = exception.message;
      error = { name: exception.name, stack: exception.stack };
    }

    const errorResponse: ApiResponse = {
      status: 'error',
      message,
      error: process.env.NODE_ENV === 'development' ? error : undefined,
    };

    response.status(status).json(errorResponse);
  }
}
