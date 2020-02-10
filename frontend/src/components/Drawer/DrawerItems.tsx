import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import React from 'react';
import { menuItems } from './menuItems';
import { useBusinessArea } from '../../hooks/useBusinessArea';

const Text = styled(ListItemText)`
  .MuiTypography-body1 {
    color: #233944;
    font-size: 14px;
    font-weight: 500;
    line-height: 16px;
  }
`;
const Icon = styled(ListItemIcon)`
  &&  {
    min-width: 0;
    padding-right: ${({theme})=>theme.spacing(4)}px;
  }
`;

interface Props {
  currentLocation: string;
}
export function DrawerItems({ currentLocation }: Props): React.ReactElement {
  const businessArea = useBusinessArea();
  return (
    <div>
      {menuItems.map((item) => {
        return (
          <ListItem
            button
            component={Link}
            key={item.name}
            to={`/${businessArea}${item.href}`}
            selected={Boolean(item.selectedRegexp.exec(currentLocation))}
          >
            <Icon>{item.icon}</Icon>
            <Text primary={item.name} />
          </ListItem>
        );
      })}
    </div>
  );
}
