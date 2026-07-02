import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import * as bcrypt from 'bcrypt'; // Importamos bcrypt

@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  async createUser(data: any) {
    // 1. Definimos cuántas rondas de encriptación usaremos (10 es el estándar)
    const saltRounds = 10;
    
    // 2. Ciframos la contraseña
    const hashedPassword = await bcrypt.hash(data.password, saltRounds);

    // 3. Guardamos el usuario con la contraseña cifrada
    return this.prisma.users.create({
      data: {
        name: data.name,
        email: data.email,
        password: hashedPassword, // Guardamos el hash, no la contraseña original
      },
    });
  }
}