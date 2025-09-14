import React from 'react';
import { Element } from 'react-scroll';

interface ContainerProps {
    name: string;
    children: React.ReactNode;
    className?: string;
}

export function Container({ name, children, className = '' }: ContainerProps) {
    return (
        <Element name={name}>
            <section
                className={`${className} 
                mx-auto max-w-7xl px-4 py-20 flex flex-col items-center justify-center gap-6`}>
                {children}
            </section>
        </Element>


    );
}