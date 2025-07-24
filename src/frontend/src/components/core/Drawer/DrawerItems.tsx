import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import { Box, ListItemButton } from '@mui/material';
import Collapse from '@mui/material/Collapse';
import List from '@mui/material/List';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { ElementType, ReactElement, useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
  hasPermissionInModule,
  hasPermissions,
} from '../../../config/permissions';
import {
  MenuItem,
  menuItems,
  SCOPE_ALL_PROGRAMS,
  SCOPE_PROGRAM,
} from './menuItems';
import { useProgramContext } from 'src/programContext';
import { BeneficiaryGroup } from '@restgenerated/models/BeneficiaryGroup';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

const Text = styled(ListItemText)`
  .MuiTypography-body1 {
    color: #233944;
    font-size: 14px;
    font-weight: 500;
    line-height: 16px;
    margin-right: 100px;
  }
`;
const Icon = styled(ListItemIcon)`
  && {
    min-width: 40px;
  }
`;
interface SubListProps {
  open: boolean;
  component: ElementType;
}

const SubList = styled(List)<SubListProps>`
  padding-left: ${({ open }) => (open ? '32px !important' : 0)};
`;

export const ArrowIconWrapper = styled.div`
  position: absolute;
  right: -2px;
  top: 8px;
`;

interface DrawerItemsProps {
  currentLocation: string;
  open: boolean;
}
export const DrawerItems = ({
  currentLocation,
  open,
}: DrawerItemsProps): ReactElement => {
  const { baseUrl, businessArea, programId, isAllPrograms } = useBaseUrl();
  const { isSocialDctType, selectedProgram } = useProgramContext();
  const permissions = usePermissions();

  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({
        slug: businessArea,
      }),
  });

  const clearLocation = currentLocation.replace(`/${baseUrl}`, '');
  const navigate = useNavigate();
  const initialIndex = menuItems.findIndex((item) => {
    if (!item.secondaryActions) {
      return false;
    }
    return (
      item.secondaryActions.findIndex((secondaryItem) =>
        Boolean(secondaryItem.selectedRegexp.exec(clearLocation)),
      ) !== -1
    );
  });
  const [expandedItem, setExpandedItem] = useState(
    initialIndex !== -1 ? initialIndex : null,
  );

  // close nav when changing business area or program
  useEffect(() => {
    setExpandedItem(null);
  }, [baseUrl]);

  if (permissions === null || !businessAreaData) return null;

  const prepareMenuItems = (items: MenuItem[]): MenuItem[] => {
    let updatedMenuItems = [...items];
    const getIndexByName = (name: string): number =>
      updatedMenuItems.findIndex((item) => item?.name === name);
    const programDetailsIndex = getIndexByName('Programme Details');

    // When GlobalProgramFilter applied
    if (!isAllPrograms) {
      updatedMenuItems[programDetailsIndex].href = `/details/${programId}`;
    }
    updatedMenuItems = updatedMenuItems.filter((item) => {
      let isVisible = isAllPrograms
        ? item.scopes.includes(SCOPE_ALL_PROGRAMS)
        : item.scopes.includes(SCOPE_PROGRAM);
      const isSocialWorkerProgram = isSocialDctType;
      if (item.isSocialWorker === false) {
        isVisible &&= !isSocialWorkerProgram;
      } else if (item.isSocialWorker === true) {
        isVisible &&= isSocialWorkerProgram;
      }
      return isVisible;
    });
    return updatedMenuItems;
  };

  const beneficiaryGroupTransformator = (
    array: MenuItem[],
    _beneficiaryGroup: BeneficiaryGroup,
  ): MenuItem[] => {
    if (!_beneficiaryGroup) {
      return array;
    }

    return array.map((item, index) => {
      if (index === 2 && !isAllPrograms) {
        item.name = _beneficiaryGroup.name;
        if (item.secondaryActions) {
          item.secondaryActions = item.secondaryActions.map(
            (action, actionIndex) => {
              if (actionIndex === 0) {
                action.name = _beneficiaryGroup.groupLabelPlural;
              } else if (actionIndex === 1) {
                action.name = _beneficiaryGroup.memberLabelPlural;
              }
              return action;
            },
          );
        }
      }
      return item;
    });
  };

  const preparedMenuItems = beneficiaryGroupTransformator(
    prepareMenuItems(menuItems),
    selectedProgram?.beneficiaryGroup,
  );

  const { isAccountabilityApplicable } = businessAreaData;
  const flags = {
    isAccountabilityApplicable,
  };

  const getInitialHrefForCollapsible = (secondaryActions): string => {
    let resultHref = '';
    for (const item of secondaryActions) {
      if (
        item.permissionModule &&
        hasPermissionInModule(item.permissionModule, permissions)
      ) {
        resultHref = item.href;
        break;
      }
    }
    return resultHref;
  };

  return (
    <div data-cy="drawer-items">
      {preparedMenuItems?.map((item, index) => {
        if (
          item.permissionModule &&
          !hasPermissionInModule(item.permissionModule, permissions)
        )
          return null;

        if (item.permissions && !hasPermissions(item.permissions, permissions))
          return null;

        if (item.flag && !flags[item.flag]) {
          return null;
        }

        if (item.collapsable) {
          const hrefForCollapsibleItem = getInitialHrefForCollapsible(
            item.secondaryActions,
          );

          return (
            <div key={item?.name + hrefForCollapsibleItem}>
              <ListItemButton
                component={NavLink}
                data-cy={`nav-${item?.name}`}
                to={`/${baseUrl}${hrefForCollapsibleItem}`}
                onClick={() => {
                  if (index === expandedItem) {
                    setExpandedItem(null);
                  } else {
                    setExpandedItem(index);
                  }
                  if (hrefForCollapsibleItem) {
                    navigate(`/${baseUrl}${hrefForCollapsibleItem}`);
                  }
                }}
              >
                <Icon>{item.icon}</Icon>
                <Text primary={item?.name} />
                {expandedItem !== null && expandedItem === index ? (
                  <ArrowIconWrapper>
                    <ExpandLess />
                  </ArrowIconWrapper>
                ) : (
                  <ArrowIconWrapper>
                    <ExpandMore />
                  </ArrowIconWrapper>
                )}
              </ListItemButton>
              <Collapse in={expandedItem !== null && expandedItem === index}>
                <SubList open={open} component="div">
                  {item.secondaryActions &&
                    item.secondaryActions.map(
                      (secondary) =>
                        secondary.permissionModule &&
                        hasPermissionInModule(
                          secondary.permissionModule,
                          permissions,
                        ) && (
                          <ListItemButton
                            component={NavLink}
                            data-cy={`nav-${secondary.name}`}
                            key={secondary.name}
                            to={`/${baseUrl}${secondary.href}`}
                            selected={Boolean(
                              secondary.selectedRegexp.exec(clearLocation),
                            )}
                          >
                            <Icon>{secondary.icon}</Icon>
                            <Text primary={secondary.name} />
                          </ListItemButton>
                        ),
                    )}
                </SubList>
              </Collapse>
            </div>
          );
        }
        return item.external ? (
          <ListItemButton
            data-cy={`nav-${item?.name}`}
            component={NavLink}
            key={item?.name + item.href}
            to={item.href}
            target="_blank"
          >
            <Box display="flex">
              <Icon>{item.icon}</Icon>
              <Text primary={item?.name} />
            </Box>
          </ListItemButton>
        ) : (
          <ListItemButton
            data-cy={`nav-${item?.name}`}
            component={NavLink}
            key={item?.name + item.href}
            to={`/${baseUrl}${item.href}`}
            onClick={() => {
              setExpandedItem(null);
            }}
            selected={Boolean(item.selectedRegexp.exec(clearLocation))}
          >
            <Icon>{item.icon}</Icon>
            <Text primary={item?.name} />
          </ListItemButton>
        );
      })}
    </div>
  );
};
