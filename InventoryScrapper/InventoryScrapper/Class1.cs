using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using FrooxEngine;
using FrooxEngine.UIX;
using System.Reflection;
using System.Runtime.CompilerServices;
using Newtonsoft.Json;
using BaseX;

namespace FrooxEngine.LogiX
{

    [Category("LogiX/AAAA")]
    [NodeName("Scrape Invetory")]
    public class OwO : LogixNode
    {
        public Slot thingo;
        public ButtonActionTrigger actionTrigger;
        public InventoryBrowser inventory;
        HashSet<string> folderIds;
        HashSet<RecordDirectory> folders;
        System.IO.StreamWriter file;
        protected override void OnAttach()
        {
            base.OnAttach();
            //var i = this.Slot.AttachComponent<InventoryBrowser>();
            //i.OpenDefault();
            Userspace.UserspaceWorld?.RunSynchronously((Action)(() => Userspace.UserspaceWorld.GetRadiantDash().ToggleLegacyInventory()), false, (IUpdatable)null, false);
            Userspace.UserspaceWorld?.RunSynchronously((Action)(() => {
                //inventory = Userspace.UserspaceWorld.GetGloballyRegisteredComponent<InventoryBrowser>();
                Slot slot = Userspace.UserspaceWorld.RootSlot.FindChild((Slot x)=>(x.Name=="Legacy Inventory"));
                slot.GetComponent<NeosCanvasPanel>().Panel.Slot.TransferToWorld(this.Engine.WorldManager.FocusedWorld);
                //PropertyInfo itemsProperty = inventory.GetType().GetProperty("_currentItems", BindingFlags.NonPublic | BindingFlags.Instance);

                //MethodInfo currentItemsGetter = itemsProperty.GetGetMethod(nonPublic: true);

                //Dictionary<Record, InventoryItemUI> curretnItems = (Dictionary<Record, InventoryItemUI>)currentItemsGetter.Invoke(inventory, null);
            }), false, (IUpdatable)null, false);
        }

        [ImpulseTarget]
        public void Run()
        {
            Slot slot = this.World.RootSlot.FindChild((Slot x)=>(x.Name=="Legacy Inventory"));
            inventory = slot.FindChild((Slot x) => (x.Name == "Content")).FindChild((Slot x) => (x.Name == "Slot")).GetComponent<InventoryBrowser>();
            file = new System.IO.StreamWriter(@"InventoryScrap.txt");
            file.Write("[");
            folderIds = Pool.BorrowHashSet<string>();
            folders = Pool.BorrowHashSet<RecordDirectory>();
            Iterate(inventory.CurrentDirectory);
            file.Write("]");
            file.Close();
        }
        public void Iterate(RecordDirectory currentDirectory)
        {
            TaskAwaiter awaiter = currentDirectory.EnsureFullyLoaded().GetAwaiter();
            awaiter.GetResult();
            foreach (Record record in (IEnumerable<Record>)currentDirectory.Records)
            {
                //Debug.Log(record.Name);
                Debug.Log(currentDirectory.Path);
                string output = JsonConvert.SerializeObject(record);
                file.Write(output+",");
                //Debug.Log(output);
            }
            foreach (RecordDirectory subdirectory in (IEnumerable<RecordDirectory>)currentDirectory.Subdirectories)
            {
                //this._currentItems.TryGetValue(
                //inventory._currentPath.Value = directory.GetRelativePath(false);
                //if (this.World == Userspace.UserspaceWorld && this != InventoryBrowser.CurrentUserspaceInventory && InventoryBrowser.CurrentUserspaceInventory != null)
                //{
                //    InventoryBrowser.CurrentUserspaceInventory._changePath = this._currentPath.Value;
                //    InventoryBrowser.CurrentUserspaceInventory._changeOwnerId = this._currentOwnerId.Value;
                //}
                //this.StartTask((Func<Task>)(async () => await this.OpenDirectory(directory, slide).ConfigureAwait(false)));
                //inventory.OpenDirectory(directory, slide).ConfigureAwait(false));
                //inventory.Open(subdirectory, SlideSwapRegion.Slide.None);
                //MethodInfo openDirectoryMethod = inventory.GetType().GetMethod("OpenDirectory", BindingFlags.NonPublic | BindingFlags.Instance);
                //Task task = this.StartTask((Func<Task>)(async () => await ((Task)openDirectoryMethod.Invoke(inventory, new object[] { subdirectory, SlideSwapRegion.Slide.None })).ConfigureAwait(false)));
                //task.Wait();
                //string previousDir = inventory.CurrentDirectory.Path;
                //while(true)
                //{
                //    if (inventory.CurrentDirectory.Path != previousDir)
                //    {
                //        break;
                //    }
                //}
                //string folderId = subdirectory.OwnerId+":"+subdirectory.Path;
                string folderId = subdirectory.OwnerId + ":" + subdirectory.Name;
                folderId = subdirectory.IsLink ? subdirectory.LinkRecord.RecordId : folderId;
                //if (subdirectory.Path.Split('\\').Length < 1 && !folderIds.Contains(folderId))
                //if (!folders.Contains(subdirectory))
                if (!folderIds.Contains(folderId))
                {
                    //this.Iterate(i + 1);
                    folderIds.Add(folderId);
                    //folders.Add(subdirectory);
                    Iterate(subdirectory);

                }
            }
        }
    }
    //[Category("LogiX/AAAA")]
    //[NodeName("Make source touchable")]
    //public class MakeSourceTouchable : LogixNode
    //{
    //    public readonly SyncRef<Slot> slot;
    //    public readonly RelayRef<IValue<bool>> boolref;
    //    [ImpulseTarget]
    //    public void Run()
    //    {
    //        TipTouchSource touchSource = slot.Target.GetComponent<TipTouchSource>();
    //        //touchSource.LocalForceTouch = true;
    //        boolref.TrySet((IWorldElement)touchSource.LocalForceTouch);
    //    }

    //}
    
}
