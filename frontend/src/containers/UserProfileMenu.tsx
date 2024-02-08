import {
  Avatar,
  Button,
  ClickAwayListener,
  Grow,
  MenuItem,
  MenuList,
  Paper,
  Popper,
} from '@mui/material';
import * as React from 'react';
import styled from 'styled-components';
import { MeQuery } from '@generated/graphql';
import { clearCache } from '@utils/utils';
import { getClient } from '../apollo/client';

const UserProfileButton = styled(Button)`
  && {
    color: #e3e6e7;
  }
`;
const MenuButtonText = styled.span`
  margin-left: ${({ theme }) => theme.spacing(2)}px;
`;
interface UserProfileMenuProps {
  meData: MeQuery;
}
export function UserProfileMenu({
  meData,
}: UserProfileMenuProps): React.ReactElement {
  const [open, setOpen] = React.useState(false);
  const anchorRef = React.useRef<HTMLButtonElement>(null);
  // return focus to the button when we transitioned from !open -> open
  const prevOpen = React.useRef(open);
  React.useEffect(() => {
    if (prevOpen.current === true && open === false) {
      anchorRef.current.focus();
    }

    prevOpen.current = open;
  }, [open]);

  const handleToggle = (): void => {
    setOpen((previousOpen) => !previousOpen);
  };

  const handleClose = (event: React.MouseEvent<EventTarget>): void => {
    if (
      anchorRef.current &&
      anchorRef.current.contains(event.target as HTMLElement)
    ) {
      return;
    }

    setOpen(false);
  };

  const handleClearCache = async (): Promise<void> => {
    const client = await getClient();
    await clearCache(client);
  };

  const handleClearCacheAndReloadWindow = async (): Promise<void> => {
    await handleClearCache();
    window.location.reload();
  };
  const handleLogout = (event: React.MouseEvent<EventTarget>): void => {
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
    handleClose(event);
    handleClearCache();
  };
  function handleListKeyDown(event: React.KeyboardEvent): void {
    if (event.key === 'Tab') {
      event.preventDefault();
      setOpen(false);
    }
  }
  if (!meData) {
    return null;
  }

  return (
    <>
      <UserProfileButton
        ref={anchorRef}
        onClick={handleToggle}
        data-cy="menu-user-profile"
      >
        <Avatar alt={meData.me.email} src="/static/images/avatar/1.jpg" />
        <MenuButtonText> {meData.me.email}</MenuButtonText>
      </UserProfileButton>
      <Popper
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
      >
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{
              transformOrigin:
                placement === 'bottom' ? 'center top' : 'center bottom',
            }}
          >
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList
                  autoFocusItem={open}
                  id="menu-list-grow"
                  onKeyDown={handleListKeyDown}
                >
                  <MenuItem
                    onClick={handleClearCacheAndReloadWindow}
                    data-cy="menu-item-clear-cache"
                  >
                    Clear Cache
                  </MenuItem>
                  <MenuItem onClick={handleLogout} data-cy="menu-item-logout">
                    Logout
                  </MenuItem>
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
}
