// interceptors/response-transform.interceptor.ts
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Request, Response } from 'express';
import { ApiResponse } from '../interfaces/api-response.interface';

@Injectable()
export class ResponseTransformInterceptor<T>
  implements NestInterceptor<T, ApiResponse<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<ApiResponse<T>> {
    const request = context.switchToHttp().getRequest<Request>();
    const response = context.switchToHttp().getResponse<Response>();

    return next.handle().pipe(
      map((data) => {
        // Don't transform if data is already in the expected format
        if (
          data &&
          typeof data === 'object' &&
          'status' in data &&
          'message' in data
        ) {
          return data as ApiResponse<T>;
        }

        // Get the HTTP status code
        const statusCode = response.statusCode;

        // Determine success message based on HTTP method and status
        let message = 'Operation completed successfully';

        switch (request.method) {
          case 'POST':
            message =
              statusCode === 201
                ? 'Resource created successfully'
                : 'Data processed successfully';
            break;
          case 'PUT':
          case 'PATCH':
            message = 'Resource updated successfully';
            break;
          case 'DELETE':
            message = 'Resource deleted successfully';
            break;
          case 'GET':
            message = 'Data retrieved successfully';
            break;
        }

        return {
          status: 'success' as const,
          message,
          data: data as T,
        };
      }),
    );
  }
}
