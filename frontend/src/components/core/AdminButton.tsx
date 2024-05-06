import ArrowCircleRightIcon from '@mui/icons-material/ArrowCircleRight';
import * as React from 'react';


interface AdminButtonProps {
    adminUrl: string;
    [key: string]: any;
}

export const AdminButton: React.FC<AdminButtonProps> = ({
    adminUrl,
    ...otherProps
}) => {
    if (adminUrl) {
        return <a href={adminUrl}><ArrowCircleRightIcon color="primary" {...otherProps}/></a>;
    }
    return null;
};
