declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user: import('better-auth').User | null;
      session: import('better-auth').Session | null;
    }
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
}

export {};
