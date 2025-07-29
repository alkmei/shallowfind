import { Module } from '@nestjs/common';
import { AuthModule } from './auth/auth.module';
import { FirebaseAuthStrategy } from './auth/firebase/firebase.strategy';
import { APP_FILTER, APP_GUARD, APP_INTERCEPTOR } from '@nestjs/core';
import { FirebaseAuthGuard } from './auth/firebase/firebase.guard';
import { ResponseTransformInterceptor } from './common/interceptors/response-transform.interceptor';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';

@Module({
  imports: [AuthModule],
  providers: [
    FirebaseAuthStrategy,
    {
      provide: APP_INTERCEPTOR,
      useClass: ResponseTransformInterceptor,
    },
    {
      provide: APP_FILTER,
      useClass: HttpExceptionFilter,
    },
    {
      provide: APP_GUARD,
      useClass: FirebaseAuthGuard,
    },
  ],
})
export class AppModule {}
