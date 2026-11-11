import os, random, shutil, subprocess, threading, sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

EXTS={".mp4",".mov",".mkv"}
TITLES=["Video Project","Untitled Clip","Media Collection","Recorded Session","Creative Footage","Personal Archive","Sample Video","Edited Sequence"]
COMMENTS=["Personal media library","Video metadata refreshed","Organized media collection","Processed video file"]
ARTISTS=["Studio Media","Personal Archive","Video Editor","Media Creator","Local Library"]

def ffmpeg_path():
    exe="ffmpeg.exe" if os.name=="nt" else "ffmpeg"
    root=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))
    for p in (root/"tools"/exe, Path(__file__).resolve().parent/"tools"/exe):
        if p.exists(): return str(p)
    return shutil.which("ffmpeg")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Auto Metadata Video")
        self.geometry("720x500"); self.minsize(620,420); self.configure(bg="#101827")
        self.files=[]; self.out=""
        s=ttk.Style(self); s.theme_use("clam")
        s.configure("TFrame",background="#101827"); s.configure("TLabel",background="#101827",foreground="#e8eef8",font=("Segoe UI",10))
        s.configure("Head.TLabel",font=("Segoe UI",20,"bold"),foreground="white")
        s.configure("Treeview",rowheight=26)
        root=ttk.Frame(self,padding=18); root.pack(fill="both",expand=True)
        ttk.Label(root,text="Auto Metadata Video",style="Head.TLabel").pack(anchor="w")
        ttk.Label(root,text="Pengacak metadata MP4 • MOV • MKV | Windows x64").pack(anchor="w",pady=(3,14))
        bar=ttk.Frame(root); bar.pack(fill="x",pady=5)
        ttk.Button(bar,text="Tambah Video",command=self.add).pack(side="left")
        ttk.Button(bar,text="Tambah Folder",command=self.folder).pack(side="left",padx=7)
        ttk.Button(bar,text="Hapus Pilihan",command=self.remove).pack(side="left")
        self.tree=ttk.Treeview(root,columns=("file","status"),show="headings",selectmode="extended")
        self.tree.heading("file",text="File video"); self.tree.heading("status",text="Status")
        self.tree.column("file",width=500); self.tree.column("status",width=120,anchor="center")
        self.tree.pack(fill="both",expand=True,pady=8)
        row=ttk.Frame(root); row.pack(fill="x")
        ttk.Button(row,text="Pilih Folder Hasil",command=self.pick).pack(side="left")
        self.outlabel=ttk.Label(row,text="Folder belum dipilih"); self.outlabel.pack(side="left",padx=8)
        self.keep=tk.BooleanVar(value=True)
        ttk.Checkbutton(root,text="Simpan sebagai file baru (jaga file asli)",variable=self.keep).pack(anchor="w",pady=8)
        self.prog=ttk.Progressbar(root,maximum=100); self.prog.pack(fill="x")
        self.status=ttk.Label(root,text="Siap digunakan."); self.status.pack(anchor="w",pady=5)
        ttk.Button(root,text="ACAK METADATA & PROSES",command=self.start).pack(fill="x",pady=8)
        ttk.Label(root,text="Mengacak title, comment, artist, album, genre. Tidak mengubah codec, resolusi, durasi, GPS, atau tanggal rekaman.",wraplength=680).pack(anchor="w",pady=5)

    def add_paths(self,paths):
        for x in paths:
            p=Path(x)
            if p.suffix.lower() in EXTS and str(p) not in self.files:
                self.files.append(str(p)); self.tree.insert("", "end",iid=str(p),values=(p.name,"Menunggu"))
    def add(self):
        self.add_paths(filedialog.askopenfilenames(filetypes=[("Video","*.mp4 *.mov *.mkv")]))
    def folder(self):
        d=filedialog.askdirectory()
        if d: self.add_paths([str(p) for p in Path(d).rglob("*") if p.is_file()])
    def remove(self):
        for x in self.tree.selection():
            self.tree.delete(x)
            if x in self.files:self.files.remove(x)
    def pick(self):
        d=filedialog.askdirectory()
        if d:self.out=d; self.outlabel.config(text=d)
    def start(self):
        tool=ffmpeg_path()
        if not self.files: messagebox.showwarning("Video kosong","Tambahkan video terlebih dahulu."); return
        if not self.out: messagebox.showwarning("Folder hasil","Pilih folder hasil."); return
        if not tool: messagebox.showerror("FFmpeg tidak tersedia","Komponen FFmpeg tidak ditemukan."); return
        self.prog["value"]=0; self.prog["maximum"]=len(self.files)
        threading.Thread(target=self.work,args=(tool,),daemon=True).start()
    def work(self,tool):
        success=0; total=len(self.files)
        for i,src in enumerate(self.files,1):
            p=Path(src); dest=Path(self.out)/(p.stem+"_metadata"+p.suffix if self.keep.get() else p.name)
            tags={"title":random.choice(TITLES),"comment":random.choice(COMMENTS),"artist":random.choice(ARTISTS),
                  "album":"Media Collection "+str(random.randint(1,99)),"genre":random.choice(["Other","Documentary","Personal Video","Miscellaneous"])}
            cmd=[tool,"-hide_banner","-loglevel","error","-y","-i",str(p),"-map","0","-map_metadata","0","-c","copy"]
            for k,v in tags.items():cmd += ["-metadata",f"{k}={v}"]
            cmd += [str(dest)]
            try:
                r=subprocess.run(cmd,capture_output=True,text=True,timeout=7200)
                good=(r.returncode==0)
            except Exception: good=False
            if good:success+=1
            self.after(0,lambda path=str(p),st=("Berhasil" if good else "Gagal"):self.tree.set(path,"status",st))
            self.after(0,lambda n=i:self.prog.configure(value=n))
        self.after(0,lambda:self.status.config(text=f"Selesai: {success}/{total} video berhasil."))
        self.after(0,lambda:messagebox.showinfo("Selesai",f"{success} dari {total} video berhasil diproses."))
if __name__=="__main__": App().mainloop()
