import React from 'react';

interface PageContainerProps {
    children: React.ReactNode;
    className?: string;
}

export function PageContainer({ children, className = '' }: PageContainerProps) {
    return (
        <div
            className={`
            relative flex flex-col justify-center items-center 
            min-h-screen lg:h-screen
            max-w-5xl mx-auto
            gap-8
            p-2 lg:p-0
            pt-12 lg:pt-0
            ${className}`}>
            {children}
        </div>
    );
}


/*  max-w-5xl  gap-8  */