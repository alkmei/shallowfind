import { Module } from '@nestjs/common';
import { PassportModule } from '@nestjs/passport';
import { FirebaseAuthStrategy } from './firebase/firebase.strategy';
import { FirebaseAuthGuard } from './firebase/firebase.guard';

@Module({
  imports: [PassportModule],
  providers: [FirebaseAuthStrategy, FirebaseAuthGuard],
  exports: [FirebaseAuthGuard],
})
export class AuthModule {}
