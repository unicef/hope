import Collapse from '@material-ui/core/Collapse';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import { Link } from 'react-router-dom';
import React from 'react';
import { menuItems } from './menuItems';
import { useBusinessArea } from '../../hooks/useBusinessArea';

interface Props {
  currentLocation: string;
  handleItemCollapse: (index: number) => void;
  itemsCollapse: { id: number, open: boolean }[]
}
export function DrawerItems({ currentLocation, handleItemCollapse, itemsCollapse }: Props): React.ReactElement {
  const businessArea = useBusinessArea();
  const testBoolean = true;

  const checkCollapse = (index: number): boolean => {
    console.log(itemsCollapse)
    if (!itemsCollapse) return false;
    if (itemsCollapse.find(x => x.id === index)) return itemsCollapse.find(x => x.id === index).open;
    return false;
  }

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
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
            {itemsCollapse && itemsCollapse[index] ? <ExpandLess /> : <ExpandMore />}
          </ListItem>
            <Collapse in={checkCollapse(index)}>
              <List component="div" disablePadding>
                { item.secondaryActions && item.secondaryActions.map(secondary => (
                  <ListItem
                  button
                  component={Link}
                  key={secondary.name}
                  to={`/${businessArea}${secondary.href}`}
                  selected={Boolean(secondary.selectedRegexp.exec(currentLocation))}
                >
                  <ListItemIcon>{secondary.icon}</ListItemIcon>
                  <ListItemText primary={secondary.name} />
                </ListItem>
                
                )
                )}
              </List>
            </Collapse>
            </>
          )
        }
          return (
          <ListItem
            button
            component={Link}
            key={item.name}
            to={`/${businessArea}${item.href}`}
            selected={Boolean(item.selectedRegexp.exec(currentLocation))}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.name} />
          </ListItem>
        );
      })}
    </div>
  );
}
