import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import React from 'react';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { menuItems } from './menuItems';

const Text = styled(ListItemText)`
  .MuiTypography-body1 {
    color: #233944;
    font-size: 14px;
    font-weight: 500;
    line-height: 16px;
  }
`;
const Icon = styled(ListItemIcon)`
  && {
    min-width: 0;
    padding-right: ${({ theme }) => theme.spacing(4)}px;
  }
`;

interface Props {
  currentLocation: string;
  handleItemCollapse: (index: number) => void;
  itemsCollapse: { id: number; open: boolean }[];
}
export function DrawerItems({
  currentLocation,
  handleItemCollapse,
  itemsCollapse,
}: Props): React.ReactElement {
  const businessArea = useBusinessArea();

  const checkCollapse = (index: number): boolean => {
    if (!itemsCollapse) return false;
    if (itemsCollapse.find((x) => x.id === index))
      return itemsCollapse.find((x) => x.id === index).open;
    return false;
  };

  return (
    <div>
      {menuItems.map((item, index) => {
        if (item.collapsable) {
          return (
            <>
              <ListItem
                button
                onClick={() => handleItemCollapse(index)}
                component={Link}
                key={item.name}
                to={`/${businessArea}${item.href}`}
                selected={Boolean(item.selectedRegexp.exec(currentLocation))}
              >
                <Icon>{item.icon}</Icon>
                <Text primary={item.name} />
                {itemsCollapse && itemsCollapse[index] ? (
                  <ExpandLess />
                ) : (
                  <ExpandMore />
                )}
              </ListItem>
              <Collapse in={checkCollapse(index)}>
                <List component='div' style={{ paddingLeft: '40px' }}>
                  {item.secondaryActions &&
                    item.secondaryActions.map((secondary) => (
                      <ListItem
                        button
                        component={Link}
                        key={secondary.name}
                        to={`/${businessArea}${secondary.href}`}
                        selected={Boolean(
                          secondary.selectedRegexp.exec(currentLocation),
                        )}
                      >
                        <Icon>{secondary.icon}</Icon>
                        <Text primary={secondary.name} />
                      </ListItem>
                    ))}
                </List>
              </Collapse>
            </>
          );
        }
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
