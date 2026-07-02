import { Module } from '@nestjs/common';
import { UsersService } from './users.service';
import { PrismaModule } from '../prisma/prisma.module'; // Importa el módulo

@Module({
  imports: [PrismaModule], // Añádelo aquí
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}