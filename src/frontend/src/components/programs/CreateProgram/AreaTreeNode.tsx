import { AreaTree } from '@restgenerated/models/AreaTree';

export class AreaTreeNode {
  id: string;

  checked: boolean | 'indeterminate';

  name: string;

  parent: AreaTreeNode;

  children: AreaTreeNode[];

  constructor(id: string, name: string) {
    this.id = id;
    this.name = name;
    this.children = [];
    this.checked = false; // false, true, 'indeterminate'
  }

  addChild(child: AreaTreeNode): void {
    this.children.push(child);
    // eslint-disable-next-line no-param-reassign
    child.parent = this;
  }

  updateCheckStatus(): void {
    if (this.children.length === 0) return;

    const allChecked = this.children.every((child) => child.checked === true);
    const someChecked = this.children.some(
      (child) => child.checked === true || child.checked === 'indeterminate',
    );

    if (allChecked) {
      this.checked = true;
    } else if (someChecked) {
      this.checked = 'indeterminate';
    } else {
      this.checked = false;
    }

    if (this.parent) {
      this.parent.updateCheckStatus();
    }
  }

  updateCheckStatusFromRoot(): void {
    this.updateCheckStatus();
    if (this.parent) {
      this.parent.updateCheckStatusFromRoot();
    }
  }

  toggleCheck(): void {
    if (this.checked === 'indeterminate') {
      this.setChecked(true);
    } else {
      const newState = !this.checked;
      this.setChecked(newState);
    }
  }

  setChecked(newState): void {
    this.checked = newState;
    this.children.forEach((child) => child.setChecked(newState));
    this.updateCheckStatusFromRoot();
  }

  getSelectedIds(): string[] {
    const selectedIds: string[] = [];
    this.traverse((node) => {
      if (node.checked === true) {
        selectedIds.push(node.id);
      }
    });
    return selectedIds;
  }

  static getAllSelectedIds(nodes: AreaTreeNode[]): string[] {
    const selectedIds: string[] = [];
    nodes.forEach((node) => {
      selectedIds.push(...node.getSelectedIds());
    });
    return selectedIds;
  }

  // Private method to traverse the tree
  private traverse(callback: (node: AreaTreeNode) => void): void {
    callback(this);
    this.children.forEach((child) => child.traverse(callback));
  }

  static buildTree(
    areas: AreaTree[],
    selectedIds: string[] = [],
  ): AreaTreeNode[] {
    const createNode = (
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      area: any,
      parent: AreaTreeNode | null,
    ): AreaTreeNode => {
      const node = new AreaTreeNode(area.id, area.name);
      if (selectedIds.includes(area.id)) {
        node.checked = true;
      }
      node.parent = parent;

      if (area.areas) {
        area.areas.forEach((childArea) => {
          const childNode = createNode(childArea, node);
          node.addChild(childNode);
        });
      }

      node.updateCheckStatusFromRoot();

      return node;
    };

    return areas.map((area) => createNode(area, null));
  }

  public clearChecks() {
    this.checked = false;
    this.children.forEach((node) => node.clearChecks());
  }
}
