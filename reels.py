import os, sys, json, time, subprocess, shutil, tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
CREAM="#F6F0E1"; NAVY="#0B1F3A"; TEAL="#0E8C8C"; GREEN="#2BB673"; WHITE="#FFFFFF"; SAND="#D9CFB4"; WM="#EBE1C8"
FD=os.environ.get("FONT_DIR","fonts")+"/"
BOLD=FD+"Poppins-Bold.ttf"; MED=FD+"Poppins-Medium.ttf"; REG=FD+"Poppins-Regular.ttf"
def F(p,s): return ImageFont.truetype(p,int(s))

def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def fit(d,text,path,maxw,maxh,smax,smin,sp=1.18):
    s=smax
    while s>=smin:
        f=F(path,s); lines=wrap(d,text,f,maxw)
        h=len(lines)*s*sp
        if h<=maxh and all(d.textlength(l,font=f)<=maxw for l in lines): return f,lines,s,h
        s-=4
    f=F(path,smin); lines=wrap(d,text,f,maxw); return f,lines,smin,len(lines)*smin*sp

def draw_lines(d,lines,f,x,y,s,color,sp=1.18):
    for i,l in enumerate(lines): d.text((x,y+i*s*sp),l,font=f,fill=color)

def logo(size):
    S=size*4; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im); c=S/2
    d.ellipse([0,0,S-1,S-1],fill=NAVY)
    r=S*0.04; d.ellipse([r,r,S-1-r,S-1-r],fill=CREAM)
    r2=S*0.09; d.ellipse([r2,r2,S-1-r2,S-1-r2],outline=TEAL,width=int(S*0.025))
    fb=ImageFont.truetype(BOLD,int(S*0.22))
    d.text((c,S*0.36),"GBP",font=fb,fill=NAVY,anchor="mm")
    d.text((c,S*0.56),"USD",font=fb,fill=TEAL,anchor="mm")
    # rising arrow under text
    pts=[(S*0.28,S*0.80),(S*0.40,S*0.73),(S*0.48,S*0.77),(S*0.64,S*0.67)]
    d.line(pts,fill=GREEN,width=int(S*0.035),joint="curve")
    d.polygon([(S*0.71,S*0.62),(S*0.62,S*0.73),(S*0.58,S*0.62)],fill=GREEN)
    return im.resize((size,size),Image.LANCZOS)
LOGO=None

def base(part,idx,wm=None):
    im=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(im)
    d.ellipse([620,-260,1300,420],fill="#EFE7D0")
    if wm: d.text((760,520),wm,font=F(BOLD,760),fill=WM,anchor="mm")
    global LOGO
    if LOGO is None: LOGO=logo(120)
    im.paste(LOGO,(60,80),LOGO)
    d.text((200,100),"GBPUSD RESEARCH",font=F(BOLD,34),fill=NAVY)
    d.text((200,146),"@gbpusd_research",font=F(MED,28),fill=TEAL)
    d.rounded_rectangle([760,100,1020,172],radius=36,fill=NAVY)
    d.text((890,136),f"PART {part}/10",font=F(BOLD,34),fill=CREAM,anchor="mm")
    segw=(960-4*12)/5
    for i in range(5):
        x=60+i*(segw+12); d.rounded_rectangle([x,232,x+segw,242],radius=5,fill=TEAL if i<=idx else SAND)
    # footer
    d.rounded_rectangle([60,1620,1020,1740],radius=60,fill=NAVY)
    t="Follow @gbpusd_research"; f=F(BOLD,46); tw=d.textlength(t,font=f)
    x0=(W-tw)/2+30
    d.polygon([(x0-76,1682),(x0-34,1682),(x0-55,1654)],fill=GREEN)
    d.rectangle([x0-62,1680,x0-48,1708],fill=GREEN)
    d.text((x0,1680),t,font=f,fill=CREAM,anchor="lm")
    return im,d

def arrow(d,x,y,s,col):
    d.rectangle([x,y-s*0.12,x+s*0.7,y+s*0.12],fill=col)
    d.polygon([(x+s*0.6,y-s*0.4),(x+s,y),(x+s*0.6,y+s*0.4)],fill=col)

def slide_hook(R):
    im,d=base(R["n"],0)
    d.text((60,310),R["eyebrow"],font=F(BOLD,36),fill=TEAL)
    f,lines,s,h=fit(d,R["hook"],BOLD,960,520,124,70,1.12)
    fs,sl,ss,sh=fit(d,R["sub"],MED,960,200,50,36,1.25)
    gh=h+48+sh; y=380+(620-gh)/2
    draw_lines(d,lines,f,60,y,s,NAVY,1.12)
    draw_lines(d,sl,fs,60,y+h+48,ss,TEAL,1.25)
    d.rounded_rectangle([60,1060,1020,1560],radius=36,fill=WHITE,outline=SAND,width=3)
    d.text((110,1100),"IN THIS REEL",font=F(BOLD,34),fill=TEAL)
    for i,p in enumerate(R["preview"]):
        yy=1200+i*118
        d.ellipse([110,yy,174,yy+64],fill=GREEN)
        d.text((142,yy+33),str(i+1),font=F(BOLD,36),fill=WHITE,anchor="mm")
        fp,pl,ps,ph=fit(d,p,MED,780,100,50,32,1.15)
        draw_lines(d,pl,fp,204,yy+32-ph/2,ps,NAVY,1.15)
    return im

def slide_beat(R,i):
    head,note=R["beats"][i]
    im,d=base(R["n"],i+1,wm=str(i+1))
    d.rounded_rectangle([60,312,84,360],radius=8,fill=GREEN)
    d.text((104,336),f"BEAT {i+1} OF 3",font=F(BOLD,38),fill=TEAL,anchor="lm")
    f,lines,s,h=fit(d,head,BOLD,960,560,112,60,1.14)
    y=400+(580-h)/2
    draw_lines(d,lines,f,60,y,s,NAVY,1.14)
    d.rounded_rectangle([60,1020,1020,1560],radius=36,fill=WHITE,outline=SAND,width=3)
    d.rounded_rectangle([60,1020,84,1560],radius=12,fill=TEAL)
    d.text((124,1062),"WHY IT MATTERS",font=F(BOLD,34),fill=TEAL)
    fn,nl,ns,nh=fit(d,note,MED,840,380,56,34,1.3)
    draw_lines(d,nl,fn,124,1130+(400-nh)/2,ns,NAVY,1.3)
    return im

def slide_final(R):
    im,d=base(R["n"],4)
    d.rounded_rectangle([60,310,1020,1010],radius=40,fill=NAVY)
    q=R.get("quote")
    if q:
        text,who,label=q
    else:
        text,who,label=R["takeaway"],None,"TAKEAWAY"
        text=text
    if q and label=="quote": d.text((110,330),"\u201C",font=F(BOLD,260),fill=GREEN)
    else: d.text((110,365),label if label!="quote" else "",font=F(BOLD,36),fill=GREEN)
    body=text
    f,lines,s,h=fit(d,body,BOLD,860,330,110,40,1.2)
    top,bot=(540,870) if (q and label=="quote") else (420,880)
    draw_lines(d,lines,f,110,top+(bot-top-h)/2,s,CREAM,1.2)
    if who: d.text((110,940),"\u2014 "+who,font=F(BOLD,42),fill=GREEN,anchor="lm")
    d.rounded_rectangle([60,1070,1020,1560],radius=40,fill=TEAL)
    d.text((110,1130),"NEXT",font=F(BOLD,40),fill=CREAM)
    arrow(d,230,1152,56,GREEN)
    fn,nl,ns,nh=fit(d,R["next"],BOLD,860,300,78,44,1.2)
    draw_lines(d,nl,fn,110,1210+(300-nh)/2,ns,WHITE,1.2)
    return im


HERE=os.path.dirname(os.path.abspath(__file__))
STATE=os.environ.get("STATE_FILE",os.path.join(HERE,"state.json"))
CONTENT=os.path.join(HERE,"content.json")
GRAPH=os.environ.get("GRAPH_VERSION","v25.0")
GRAPH_BASE=os.environ.get("GRAPH_BASE","https://graph.facebook.com")
RUPLOAD_BASE=os.environ.get("RUPLOAD_BASE","https://rupload.facebook.com")
TZ=ZoneInfo(os.environ.get("POST_TZ","Europe/London"))
HOUR_FROM=int(os.environ.get("HOUR_FROM","6"))
HOUR_TO=int(os.environ.get("HOUR_TO","22"))
FORCE=os.environ.get("FORCE")=="1"
DRY=os.environ.get("DRY_RUN")=="1"
POLL_SECONDS=int(os.environ.get("POLL_SECONDS","15"))
FONT_BASE="https://github.com/google/fonts/raw/main/ofl/poppins/"

def now_london(): return datetime.now(TZ)

def http(method,url,tries=4,**kw):
    """requests with retries on network errors and 5xx/429. 4xx errors are returned for the caller to report."""
    last=None
    for a in range(tries):
        try:
            if "data" in kw and hasattr(kw["data"],"seek"): kw["data"].seek(0)
            r=requests.request(method,url,timeout=kw.pop("timeout",120),**kw)
            if r.status_code in (429,500,502,503,504) and a<tries-1:
                time.sleep(2**a*3); continue
            return r
        except (requests.ConnectionError,requests.Timeout) as e:
            last=e
            if a<tries-1: time.sleep(2**a*3)
    raise RuntimeError(f"network error calling {url.split('?')[0]}: {last}")

def ok(r):
    try: j=r.json() if r.text else {}
    except ValueError: j={"raw":r.text[:300]}
    if r.status_code>=400 or (isinstance(j,dict) and "error" in j):
        msg=j.get("error",j) if isinstance(j,dict) else j
        raise RuntimeError(f"{r.request.method} {r.url.split('?')[0]} -> HTTP {r.status_code}: {json.dumps(msg)[:600]}")
    return j

def ensure_fonts():
    d=os.environ.get("FONT_DIR","fonts"); os.makedirs(d,exist_ok=True)
    for f in ("Poppins-Bold.ttf","Poppins-Medium.ttf","Poppins-Regular.ttf"):
        p=os.path.join(d,f)
        if not os.path.exists(p) or os.path.getsize(p)<10000:
            r=http("GET",FONT_BASE+f); r.raise_for_status()
            open(p,"wb").write(r.content)

def render_reel(item,out):
    tmp=tempfile.mkdtemp()
    slides=[slide_hook(item)]+[slide_beat(item,i) for i in range(3)]+[slide_final(item)]
    paths=[]
    for i,im in enumerate(slides):
        p=os.path.join(tmp,f"s{i+1}.png"); im.save(p); paths.append(p)
    lst=os.path.join(tmp,"list.txt")
    with open(lst,"w") as f:
        for p in paths: f.write(f"file '{p}'\nduration 3.5\n")
        f.write(f"file '{paths[-1]}'\n")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,
        "-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-vf","fps=30,format=yuv420p",
        "-c:v","libx264","-preset","medium","-crf","18","-c:a","aac","-shortest","-t","17.5",
        "-movflags","+faststart",out],check=True)
    shutil.rmtree(tmp,ignore_errors=True)

def resolve_credentials():
    """Returns (ig_user_id, token). ACCESS_TOKEN may be a Page token (best, never expires) or a user token.
    IG_USER_ID is optional: if missing it is looked up from the token."""
    tok=os.environ.get("ACCESS_TOKEN","").strip()
    uid=os.environ.get("IG_USER_ID","").strip()
    if not tok: raise RuntimeError("ACCESS_TOKEN secret is missing. See README step C.")
    base=f"{GRAPH_BASE}/{GRAPH}"
    if uid: return uid,tok
    me=ok(http("GET",f"{base}/me",params={"fields":"id,name,instagram_business_account","access_token":tok}))
    if me.get("instagram_business_account"):
        return me["instagram_business_account"]["id"],tok
    accts=ok(http("GET",f"{base}/me/accounts",params={"fields":"name,access_token,instagram_business_account","access_token":tok}))
    for a in accts.get("data",[]):
        if a.get("instagram_business_account"):
            print("Using Facebook Page:",a.get("name"))
            return a["instagram_business_account"]["id"],a["access_token"]
    raise RuntimeError("No Instagram Business account found for this token. Check the Instagram is linked to a Facebook Page and the token has pages_show_list and instagram_basic.")

def check_connection():
    uid,tok=resolve_credentials(); base=f"{GRAPH_BASE}/{GRAPH}"
    info=ok(http("GET",f"{base}/{uid}",params={"fields":"username,media_count","access_token":tok}))
    print(f"OK: connected to Instagram @{info.get('username')} (id {uid}), {info.get('media_count')} posts so far.")
    try:
        q=ok(http("GET",f"{base}/{uid}/content_publishing_limit",params={"fields":"quota_usage,config","access_token":tok}))
        print("Publishing quota (24h):",json.dumps(q.get("data",q)))
    except Exception as e:
        print("Could not read publishing quota (not fatal):",e)
    print("Connection is ready. Run the Post reel workflow with force=1 to post the first reel.")

def publish(path,caption):
    uid,tok=resolve_credentials(); base=f"{GRAPH_BASE}/{GRAPH}"
    if len(caption)>2200: raise RuntimeError("caption longer than 2200 characters")
    j=ok(http("POST",f"{base}/{uid}/media",data={"media_type":"REELS","upload_type":"resumable",
        "caption":caption,"share_to_feed":"true","access_token":tok}))
    cid=j["id"]; uri=j.get("uri") or f"{RUPLOAD_BASE}/ig-api-upload/{GRAPH}/{cid}"
    size=os.path.getsize(path)
    with open(path,"rb") as f:
        ok(http("POST",uri,headers={"Authorization":"OAuth "+tok,"offset":"0","file_size":str(size)},data=f,timeout=300))
    status=None
    for _ in range(60):
        st=ok(http("GET",f"{base}/{cid}",params={"fields":"status_code,status","access_token":tok}))
        status=st.get("status_code"); print("container status:",status)
        if status=="FINISHED": break
        if status in ("ERROR","EXPIRED"): raise RuntimeError(f"Instagram rejected the video: {st}")
        time.sleep(POLL_SECONDS)
    else: raise RuntimeError(f"container did not finish in time (last status {status})")
    res=ok(http("POST",f"{base}/{uid}/media_publish",data={"creation_id":cid,"access_token":tok}))
    print("published media id:",res.get("id")); return res

def in_window(dt): return HOUR_FROM<=dt.hour<=HOUR_TO

def load_state():
    try:
        st=json.load(open(STATE))
        st.setdefault("next_index",0); st.setdefault("last_slot","")
        return st
    except Exception: return {"next_index":0,"last_slot":""}

def save_state(st):
    tmp=STATE+".tmp"; json.dump(st,open(tmp,"w"),indent=1); os.replace(tmp,STATE)

def main():
    if "--check" in sys.argv: return check_connection()
    now=now_london(); slot=now.strftime("%Y-%m-%d-%H")
    if not FORCE and not in_window(now):
        print(f"{now:%H:%M} London is outside {HOUR_FROM}:00-{HOUR_TO}:59. Nothing to do."); return
    st=load_state()
    if not FORCE and st.get("last_slot")==slot:
        print("Already posted in this hour slot."); return
    items=json.load(open(CONTENT,encoding="utf-8"))
    i=st["next_index"]
    if i>=len(items):
        print("All reels have been posted. Ask Claude for the next series."); return
    item=items[i]
    print(f"Reel {i+1}/{len(items)}: Series {item['series']} Part {item['n']} - {item['hook']}")
    ensure_fonts()
    out=os.path.join(tempfile.gettempdir(),"reel.mp4")
    render_reel(item,out)
    if DRY:
        print("DRY_RUN: rendered",out,os.path.getsize(out),"bytes"); return
    publish(out,item["caption"])
    st["next_index"]=i+1; st["last_slot"]=slot
    save_state(st)

if __name__=="__main__":
    try: main()
    except Exception as e:
        print("ERROR:",e); sys.exit(1)
