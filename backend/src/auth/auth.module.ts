import { Module } from '@nestjs/common';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { UsersModule } from '../users/users.module'; // Importa UsersModule

@Module({
  imports: [UsersModule], // Importa aquí
  controllers: [AuthController],
  providers: [AuthService],
})
export class AuthModule {}