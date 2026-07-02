import { Injectable, OnModuleInit } from '@nestjs/common';
// Importa desde la ruta donde Prisma generó el código
import { PrismaClient } from '../generated/prisma'; 

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  constructor() {
    super({
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });
  }

  async onModuleInit() {
    // Si sigue dando error en $connect, asegúrate de que el cliente se generó bien
    await this.$connect();
  }
}