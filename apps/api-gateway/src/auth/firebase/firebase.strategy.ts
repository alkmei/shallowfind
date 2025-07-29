import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, ExtractJwt } from 'passport-firebase-jwt';
import { admin } from '../../config/firebase.config';

@Injectable()
export class FirebaseAuthStrategy extends PassportStrategy(
  Strategy,
  'firebase-auth',
) {
  constructor() {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
    });
  }

  async validate(token: string) {
    try {
      const firebaseUser = await admin.auth().verifyIdToken(token, true);

      if (!firebaseUser) {
        throw new UnauthorizedException();
      }

      return firebaseUser;
    } catch (error) {
      console.log('Token verification failed:', error);
      throw new UnauthorizedException(error.message);
    }
  }
}
