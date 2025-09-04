import { z } from 'zod/v4';

export const registerSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.email(),
  password: z.string().min(6).max(100)
});

export type RegisterSchema = typeof registerSchema;
