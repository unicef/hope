import ArrowCircleRightIcon from '@mui/icons-material/ArrowCircleRight';
import { useCachedMe } from '@hooks/useCachedMe';
import * as React from 'react';


interface AdminButtonProps {
    adminUrl: string;
    [key: string]: any;
}

export const AdminButton: React.FC<AdminButtonProps> = ({
    adminUrl,
    ...otherProps
}) => {
    const { data } = useCachedMe();
    const isSuperUser = data.me.isSuperuser;

    if (isSuperUser) {
        return <a href={adminUrl}><ArrowCircleRightIcon color="primary" {...otherProps}/></a>;
    }
    return null;
};
