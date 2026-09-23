export interface Password {
    value: string;
    source: 'cache' | 'generated';
}

export interface Policy {
    id: string;
    name: string;
    minLength: number;
    maxLength: number;
    requiresSpecialChars: boolean;
}

export interface PasswordHistory {
    id: string;
    password: string;
    generatedAt: Date;
}