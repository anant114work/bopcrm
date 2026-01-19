from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from leads.models import TeamMember

class Command(BaseCommand):
    help = 'Import all 321 team members from Excel data with user accounts'

    def handle(self, *args, **options):
        # Clear existing data
        TeamMember.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        
        # Excel data as provided - all 321 members
        excel_data = """Aarti sharma	aarti.sharma@boprealty.com	7669275936	Mukul grover	BROKER	
ABHIMANYU MEHRA	ABHIMANYU.MEHRA@BOPREALTY.COM	9582201434	gaurav gandhi	Sales Manager - T4	
Abhishek gg	Abhishek@boprealty.com	9711344640	sandeep sethi gurugram	Sales Manager - T4	
Abhishek singh rajput	abhirewarikhera@gmail.com	8685815058	sandeep sethi gurugram	Sales Manager - T4	
Abhishek Choudhary	Abhishekkchoudhary726@gmail.com	7065252433	Yash Sharma	Sales Manager - T4	
ABHISHEK KUMAR PM	ABHISHEK.KUMAR@BOPREALTY.COM	9711141023	payal	Sales Executive - T5	
ABHISHEK prajapati	ABHISHEKPRAJAPATI248@GMAIL.COM	9044497237	AMIT KOHLI	Sales Manager - T4	
Abhishek Tanwar	Abhishektanwar3636@gmail.com	9911030299	Himanshu kumar	BROKER	
ABHISHEK VERMA	Abhishek.kumar608@yahoo.in	7011039455	ankit mavi	BROKER	
Aditya Bhadana	Aditya.Bhadana@boprealty.com	9355876240	Vishal pandey	Sales Executive - T5	
Admin	admin@gmail.com	7290001154		Admin	
AJAY PAL SINGH	AJAYPALSINGH@BOPREALTY.COM	8800134520	gaurav gandhi	Sales Manager - T4	
Ajeet chaudhary	ajeet.chaudhary@boprealty.com	8979167613	Awadesh pateriya	BROKER	
AJEET PRATAP SINGH	AJEETPRATAPSINGH@BOPREALTY.COM	8588065313	RAVISH SINGH	Team leader - t3	
Alance Addhana	alanceaddhana1989@gmail.com	9711141377	ankit mavi	Sales Executive - T5	
Alok Gahlot	alokkumargahlot2@gmail.com	8383916450	PAWAN BHATI	BROKER	
amit bhati	amit.bhati@boprealty.com	8510808164	PRAVEEN KR SHARMA	Sales Executive - T5	
AMIT KADYAN	akumar@mybop.in	9811723442	Ankush Kadyan	BROKER	
AMIT KOHLI	AMITKOHLI@GMAIL.COM	9873422211	sandeep sethi gurugram	Sales Manager - T4	
Amit Kumar Bainsla	bainsla2323@gmail.com	9999956799	Amit Kumar Bainsla	Sales Manager - T4	
amit mavi	amit.mavi@boprealty.com	8130040959	Gaurav Mavi	Sales Director - T1	
Amit Yadav	Amit Yadav@boprealty.com	8076586732	Vishal pandey	Sales Executive - T5	
Anil rawat	anil.rawat@boprealty.com	8800490096	Commercial  User	Commercial	
Anjali pandit	Anjali.pandit@boprealty.com	9958460307	MANIISH KUMAR DABREY	Sales Executive - T5	
Anjali Singh	AnjaliSingh@BOPREALTY.COM	8588062522	JAGDISH	Sales Executive - T5	
ankit mavi	ankit.mavi@boprealty.com	9650633333	SAURAV MAVI	TEAM Head - T2	
ANKIT NAGAR	ANKIT.NAGAR@boprealty.com	9582992022	Sachin Mavi	Sales Manager - T4	
Ankur Gupta	Lifeankurgupta@gmail.com	7982339756	Priyanka Kochhar	Sales Executive - T5	
ANKUSH GAUTAM	ANKUSH.GAUTAM@BOPREALTY.COM	8929535727	Pratham Verma	Sales Executive - T5	
Ankush Kadyan	ak@mybop.in	9871627302	Gaurav Mavi	Sales Manager - T4	
anshish Gautam	ASHISHAK4789@GMAIL.COM	8826237305	RAGHU NANDAN	BROKER	
ANSHPREET	anshpreetbakshi@gmail.com	7536075675	MANISH SACHDEVA	BROKER	
Anshul Rastogi	anshulrastogi2023@gmail.com	7827525172	Abhishek Tanwar	BROKER	
anu goyal	anugoel@boprealty.com	9205098820	Ankush Kadyan	Team leader - t3	
Anuj Solanki	solankianuj203@gmail.com	8882429472	harsh yaduvanshi	BROKER	
ANURAG SINGH	ANURAG@KNOWBLER.IN	9532765290	RAHUL SIRADHANA	BROKER	
Anwar Reza khan	Anwar.Rezakhan@boprealty.com	7835003668	SHAMIM KHAN	Sales Manager - T4	
Aparna Dubey	Aparnaenterprisesco@gmail.com	9999500022	ankit mavi	Sales Manager - T4	
Aryan tomer	aryan@boprealty.com	9355077435	Ankush Kadyan	Sales Manager - T4	
Ashish	Ashish@boprealty.com	9650935754	Ashish	BROKER	
Ashok Sharma	asksha91@gmail.com	8742923616	Owais Mustafa Khan	Sales Manager - T4	
ASHUTOSH KAUSHIK	ASHUTOSHKAUSHIK@BOPREALTY.COM	7290007953	Sachin Mavi	Team leader - t3	
Atif Anwar	anwaratif41@gmail.com	7703828826	ankit mavi	Team leader - t3	
Atul Verma	av@mybop.in	9999929832		Admin	
Awadesh pateriya	Awadhesh.pateriya@boprealty.com	7834917086	Rahul solanki	Sales Manager - T4	
AYUSH SHARMA	AYUSH.SHARMA@BOPREALTY.COM	9899905522	Prince Mavi	Sales Manager - T4	
AYUSHI KRISHNATREY	AYUSHI KRISHNATREY@BOPREALTY.COM	9871880082	Suraj Kumar Sharma	Telecaller - T6	
Bhavnesh Kadyan	bhavnesh.kadyan@boprealty.com	9870115387	Ankush Kadyan	BROKER	
Bhuwan Dass	bhuwandass72@yahoo.com	9810493935	manik anand	Sales Executive - T5	
BINDU	BINDU@boprealty.com	8929251920	Anjali pandit	Sales Manager - T4	
Chandrish	chandrish@boprealty.com	9717907333	ankit mavi	BROKER	
CHAYA	CHAYA@BOPREALTY.COM	8368222392	Pratham Verma	Sales Manager - T4	
Chhavi Roy	chavvi@whiteknighta.co.in	8882204588	saba khan	Telecaller - T6	
Chhavi Tayal	propup.hr@gmail.com	9540056573	Aparna Dubey	Sales Executive - T5	
chirag jaitley	CHIRAG.JAITLEY@BOPREALTY.COM	9667434500	Gaurav Mavi	Sales Manager - T4	
Commercial  User	commercial@bop.com	9898989898	Admin	Commercial	
CS	CS.@GMAIL.COM	8114483358	komal sharma	BROKER	
debashree	ANJALIPAL@BOPREALTY.COM	9540097870	Aarti sharma	Sales Executive - T5	
deep	deep@boprealty.com	9654407879	chirag jaitley	Sales Executive - T5	
DEEPAK KASHYAP	DEEPAK@TREEINFRA.IN	9899153088	ankit mavi	BROKER	
Deepak Panwar	deepak.panwar@boprealty.com	7290001075	Sachin Mavi	BROKER	
deepak seth	vishalbro999@gmail.com	7011356405	Shweta sikdar	Sales Executive - T5	
Deepakshi tyagi	deepakshityagi28@gmail.com	9690930829	sandeep sethi gurugram	Sales Manager - T4	
Deepika	Deepika@boprealty.com	9958445033	SHARAD GOEL	Sales Executive - T5	
DEEPTI DHINGRA	DEEPTI@BOPREALTY.COM	9873181415	komal sharma	BROKER	
DEV YADAV	DEVINTERIOR10@GMAIL.COM	9958905056		Sales Executive - T5	
Devashish	Devashish@boprealty.com	7838486517	Himanshu kumar	BROKER	
Devendra Joshi	samratsharma327@gmail.com	8860100407	Kappil Sarreen	Sales Manager - T4	
Dipak Kumar	dkkumarkcs@gmail.com	9953074229	Pavan Kumar	Sales Manager - T4	
DISHA SHUKLA	DISHASHUKLAOCT@GMAIL.COM	9319042854		BROKER	
Dolly	dolly.sodhi17@gmail.com	8860100594	Romil Saxena	Sales Manager - T4	
DUSHYANT BAKSHI	DUSHYANT.BAKSHI@boprealty.com	9355891616	DUSHYANT BAKSHI	Sales Manager - T4	
GAURAV PM	GAURAV@BOPREALTY.COM	9359359659	AYUSH SHARMA	BROKER	
GAURAV BENIWAL	GAURAV.BENIWAL@BOPREALTY.COM	8929535322	Anjali pandit	Sales Executive - T5	
GAURAV BISIT	GAURAV.BISIT@boprealty.com	8929738341	Gaurav Mavi	Sales Manager - T4	
gaurav gandhi	gaurav.gandhi@boprealty.com	9873665696	Gaurav Mavi	Sales Manager - T4	
GAURAV KAUSHAL	GAURAV.KAUSHAL@boprealty.com	8929525867	Prince Mavi	Team leader - t3	
Gaurav Khanna	GAURAV.KHANNA@BOPREALTY.COM	7669423327	LALIT SAREN	Sales Manager - T4	
Gaurav Mavi	gv@mybop.in	9910266552	Admin	Sales Director - T1	
GAURAV SHARMA	INFRA.WORLD@GMAIL.COM	9717260536		BROKER	
Gaurav yadav	gaurav.yadav@gmail.com	9806231837	Pratham Verma	BROKER	
Gauri narain	naraingauri798@gmail.com	9289179438	AMIT KOHLI	Sales Executive - T5	
GAUTAM GUPTA	GAUTAM.GUPTA@boprealty.com	8506010058	SAURAV MAVI	TEAM Head - T2	
gopal pandey	gopal.pandey@boprealty.com	9811109677	komal sharma	BROKER	
HARSH	HARSH@BOPREALTY.COM	9810140207	SHARAD GOEL	Sales Manager - T4	
Harsh Choudhary	Harshhhchoudhary@gmail.com	7290049257	Tarun Virmani	Sales Manager - T4	
harsh yaduvanshi	harsh.yaduvanshi3325@gmail.com	9999353065	Himanshu kumar	Sales Manager - T4	
have on deal	haveondeal.@boprealty.com	9711360152	Ankush Kadyan	BROKER	
Himanshu kumar	Himanshu.kumar@boprealty.com	9210760063	ankit mavi	TEAM Head - T2	
hitesh et now	hitesh@boprealty.com	9599669218	komal sharma	BROKER	
HUSSAIN ABBAS	HUSSAINABBAS11072@GMAIL.COM	7870666587		BROKER	
Irfan Saifi	irfan.is2007@gmail.com	9540056437	Atif Anwar	Sales Executive - T5	
ISHANK ANAND	ISHANKANAND@BOPREALTY.COM	9711512889	Prince Mavi	Sales Manager - T4	
ISHIKA	sethishu2531@gmail.com	8368519687	MANISH SACHDEVA	BROKER	
JAGDISH	rajat.metha@boprealty.com	8800932661	Gaurav Mavi	Admin	
jagmender kumar	kabirjangra15@gmail.com	9817819228	Romil Saxena	Sales Manager - T4	
JATIN A	Jatin.654@gmail.com	9540781616	ankit mavi	Sales Manager - T4	
JATIN SHARMA	JATIN.SHARMA@BOPREALTY.COM	7669233471	RAGHU NANDAN	Sales Manager - T4	
JITENDER KHARI	JITENDERKHARI@BOPREALTY.COM	7838802259	AJAY PAL SINGH	Sales Executive - T5	
Jitendra Sharma	Sharmajatin10@gmail.com	9899944450	sandeep sethi gurugram	Sales Manager - T4	
Jyoti Rana	jbsrana98@gmail.com	8447184110	Kappil Sarreen	Sales Manager - T4	
KADYAN A	KADYAN.A@BOPREALTY.COM	9873033003	AMIT KADYAN	Sales Manager - T4	
KAJAL	KAJAL@BOPREALTY.COM	9910318368	Bhavnesh Kadyan	BROKER	
kalyan singh	kalyansingh@boprealty.com	7300762077	SHARAD GOEL	Sales Executive - T5	
KAMAL	KAMAL@GMAIL.COM	7011056874	Ankush Kadyan	BROKER	
Kanhaiya Mishra	krishmishra2233@gmail.com	7717731372		BROKER	
KAPIL KUMAR	KAPILKUMAR@boprealty.com	8377006016	Aryan tomer	Sales Executive - T5	
Kappil Sarreen	kappilsarreen@gmail.com	8851344161	Romil Saxena	Sales Manager - T4	
KHUSHI	punjabankhushi93@gmail.com	9891457591	MANISH SACHDEVA	BROKER	
Khushi Soni	Khushi.Soni@boprealty.com	7054332650	saba khan	Sales Executive - T5	
Khushpreet kaur	khushpreet@boprealty.com	9915395009	Admin	Sales Executive - T5	
komal jha	komaljha@boprealty.com	9318391029	SHARAD GOEL	Sales Executive - T5	
komal sharma	komal.sharma@boprealty.com	7290001169	Admin	Admin	
kuldeep gaur	kuldeepgaur@boprealty.com	9634501183	SHARAD GOEL	Sales Manager - T4	
kumkum	kumkumchauhan63@gmail.com	8958109563	GAURAV SHARMA	BROKER	
kushi gg	kushi@boprealty.com	8510069067	PRAVEEN KR SHARMA	Sales Executive - T5	
LALIT SAREN	LALIT.SAREN@boprealty.com	7835055318	GAUTAM GUPTA	Sales Manager - T4	
LALIT SHARMA	LALITSHARMA@boprealty.com	7835062022	payal	Sales Manager - T4	
LAVI SHARMA	LAVI SHARMA@BOPREALTY.COM	9760762190	Bhavnesh Kadyan	BROKER	
Lovekush	lovekush@boprealty.com	7838801598	Anjali pandit	Sales Executive - T5	
madhav	madhav.vij@boprealty.com	7838663778	VISHAL JOSHI	BROKER	
Madhur meet Negi	Madhur.meetNegi@boprealty.com	9557698022	Gaurav Mavi	Sales Executive - T5	
MANIISH KUMAR DABREY	MANIISH.DABREY@boprealty.com	8527105848	gaurav gandhi	Sales Manager - T4	
manik anand	MANIK@whitknight.com	9818888418	Gaurav Mavi	Sales Manager - T4	
Manish Mavi	Manish.Mavi@boprealty.com	9210455555	SAURAV MAVI	Sales Manager - T4	
MANISH SACHDEVA	manishsachdeva2009@gmail.com	9560727952	Himanshu kumar	BROKER	
manju	manju@boprealty.com	8510915589	PRAVEEN KR SHARMA	Sales Executive - T5	
manoj sethi	manojsethi@boprealty.com	9910070102	chirag jaitley	Team leader - t3	
Manoj Choudhary	manojchoudhary3806@gmail.com	8800676901	Alok Gahlot	BROKER	
Manoj Kumar	manujbhardwaj5@gmail.com	9289483332		BROKER	
Manoj pandey	Manoj pandey@boprealty.com	9990009492	Vishal pandey	Sales Manager - T4	
MANUPUSHPAM TYAGI	MANUPUSHPAMTYAGI@boprealty.com	8929525865	RAGHU NANDAN	Sales Manager - T4	
mavi	mavi@boprealty.com	9773853582	PRAVEEN MAVI	Sales Manager - T4	
Mayank Sachdeva	Mayank.Sachdeva@BOPREALTY.COM	9650920217	Mukul grover	BROKER	
MAYUR VERMA	MAYURVERMA@boprealty.com	9711141330	ISHANK ANAND	Sales Manager - T4	
MD. QAIS	MD.QAIS@GMAIL.COM	9289801791	Radhika	BROKER	
Mohammad Mehdi	syedmohd.mehdi110@gmail.com	8303464140	Romil Saxena	Team leader - t3	
Mohd Hamza	Hamzashai111102@gmail.com	7007743324	Mohammad Mehdi	Sales Executive - T5	
Mohit Chawla	mohit.chawla@gmail.com	9718152689	Awadesh pateriya	BROKER	
Mohit sharma	mohit@boprealty.com	9625004783	Aryan tomer	BROKER	
Mohit Yadav	mohity5000@gmail.com	7290001179	ankit mavi	Sales Manager - T4	
MUKESH GUPTA	MUKESH.GUPTA@boprealty.com	9873280984	RAVISH SINGH	BROKER	
mukul	mukul@boprealty.com	7678674004	Mukul grover	BROKER	
Mukul grover	mukul.grover@bopraelty.com	9911936060	Ankush Kadyan	Team leader - t3	
Nabila	nabilaquddusi91@gmail.com	9997558270		BROKER	
NADEEM	mohammad.nadeem0396@gmail.com	9999859654	Shweta sikdar	Sales Executive - T5	
Nafees Ahmed	naffees.ahmed@boprealty.com	8750399559	Awadesh pateriya	BROKER	
Narendra Balyan	neeruubalyannn@gmail.ccom	9760620744		BROKER	
Narendra Singh	narendrasngh995@gmail.com	9999401224	Rohit Kapur	TEAM Head - T2	
NARESH BHATIA	NARESH.BHATIA@BOPREALTY.COM	9810326669	RAGHU NANDAN	Team leader - t3	
Naveen Kumar	Naveen Kumar@BOPREALTY.COM	9599109073	AYUSH SHARMA	BROKER	
NEERAJ KUKREJA	NEERAJ KUKREJA@BOPREALTY.COM	9205100244	Bhavnesh Kadyan	BROKER	
Nikhar sachdeva	nikhars40@gmail.com	7900891060	MANISH SACHDEVA	BROKER	
Nikhil Tiwari	reachnikhileshi10@gmail.com	9999792678	ankit mavi	BROKER	
Nimish Goyal	nimish1270@gmail.com	7983339225	harsh yaduvanshi	BROKER	
Niraj kumar	niraj.kumar@boprealty.com	9999903547	Priyanka Jain	Sales Manager - T4	
niraj kumar singh	niraj.singh@boprealty.com	7835003892	RAGHU NANDAN	Sales Manager - T4	
niraj sharma	nirajsharma@boprealty.com	8810608976	SHARAD GOEL	Sales Executive - T5	
Nishant Maheshwari	nishant21791@gmail.com	9711852597	Atif Anwar	Sales Executive - T5	
Nitesh Singh	Nitesh.Singh@boprealty.com	7669168504	RAGHU NANDAN	Sales Manager - T4	
NITIN PANDEY	NITIN.PANDEY@BOPREALTY.COM	8169447495	SAURAV MAVI	BROKER	
Owais Mustafa Khan	owaismustafakhan05@gmail.com	8595239845	Romil Saxena	Sales Manager - T4	
Paras Mavi	Paras.mavi.1999@gmail.com	9205906280	ankit mavi	Sales Manager - T4	
Parmanand	Parmanand@boprealty.com	9873174623	Vishal pandey	Sales Executive - T5	
parush	parush@boprealty.com	8130588467	chirag jaitley	Sales Executive - T5	
Pavan Kumar	Kumarpavan89707@gmail.com	9711341024	Yash Sharma	Sales Executive - T5	
PAWAN BHATI	PAWAN.BHATI@BOPREALTY.COM	9540723070	Rajeev Nagar	Sales Manager - T4	
payal	payal@boprealty.com	9625790991	Prince Mavi	Sales Manager - T4	
piyush	piyush@boprealty.com	9667773113	chirag jaitley	Sales Executive - T5	
Piyush bhagra	Pbhagra27@gmail.com	7876913650	sandeep sethi gurugram	Sales Manager - T4	
Poonam Rawat	Poonam.Rawat@boprealty.com	9958178210	SIDHANT SHARMA	BROKER	
PRACHI KUMAR	PRACHI.KUMAR@MYBOP.IN	9650791020	Anil rawat	Commercial	
Pradhuman Kumar	pradhuman@boprealty.com	8742922372	Tarun Virmani	Sales Executive - T5	
Pratham Verma	pratham.verma@boprealty.com	7290051907	PRAVEEN MAVI	BROKER	
PRAVEEN KR SHARMA	PRAVEENKRSHARMA@BOPREALTY.COM	7838801003	gaurav gandhi	Sales Manager - T4	
Praveen Kumar	praveen.sharma4091974@gmail.com	8168546547		BROKER	
Praveen Kumar	Praveen.Kumar@gmail.com	8802437411	AYUSH SHARMA	BROKER	
Praveen Kumar srv	mrpkprem@gmail.com	9711341079	SHAMIM KHAN	Sales Executive - T5	
PRAVEEN MAVI	parveen.mavi@mybop.in	7290001190	Ankush Kadyan	Sales Manager - T4	
PRAVEEN TYAGI	PRAVEEN.TYAGI@BOPREALTY.COM	9711499215	SHARAD GOEL	Sales Executive - T5	
Prem Tamang	tprem1080@gmail.com	8588803710	Tarun Virmani	Sales Executive - T5	
Prerna	sas.realtyindia@gmail.com	9310565458	harsh yaduvanshi	BROKER	
Prince Mavi	prince.mavi@boprealty.com	9999826429	Gaurav Mavi	TEAM Head - T2	
prince panwar	princepawar95@gmail.com	7830282822	saba khan	Sales Manager - T4	
Priyanka Jain	priyanka.jain@boprealty.com	9818779907	Ankush Kadyan	Sales Manager - T4	
Priyanka Kochhar	priyankakochhar9@gmail.com	8587031626	Romil Saxena	Team leader - t3	
Puneet Bhardwaj	bhardwaj.puneetbackup@gmail.com	9711141650	Sandeep Sethi	Sales Executive - T5	
Punit Kumar	punit.kumar@boprealty.com	9650309681	Sachin Mavi	Sales Manager - T4	
Radhika	radhika.gps@outlook.com	7011967676	Ankush Kadyan	Telecaller - T6	
RAGHU NANDAN	RAGHU.NANDAN@BOPREALTY.COM	8920410474	Gaurav Mavi	TEAM Head - T2	
RAGHVENDRA SINGH	RAGHVENDRA@BOPREALTY.COM	9711365221	gaurav gandhi	Sales Manager - T4	
Raghwan	mahera.r@mybop.in	8826330262	Raghwan	Team leader - t3	
RAHUL	rahul@boprealty.com	9958218993	chirag jaitley	Sales Manager - T4	
Rahul	rahulkumarydv2710@gmail.com	9811647751	GAURAV SHARMA	Sales Executive - T5	
RAHUL BAKSHI	RAHULBAKSHI622@GMAIL.COM	9654030675	sandeep sethi gurugram	Sales Manager - T4	
RAHUL SEHGAL	RAHUL.SEHGAL70@GMAIL.COM	9818456747		BROKER	
Rahul Sharma	rahularya695@gmail.com	8588064185	Yash Sharma	Sales Manager - T4	
RAHUL SIRADHANA	rahul.siradhana@gmail.com	9899621111	RAHUL SIRADHANA	BROKER	
Rahul solanki	rs@treeglobal.in	9810338825	ankit mavi	Sales Manager - T4	
RAJ SINGH	RAJ.SINGH@boprealty.com	9355981339	NARESH BHATIA	Sales Manager - T4	
Rajat	jhopdi2011@gmail.com	8587064788	GAURAV SHARMA	Sales Executive - T5	
Rajat Mavi	Rajat.Mavi@boprealty.com	7290048657	ankit mavi	BROKER	
Rajeev Nagar	rajeev.nagar@mybop.in	9650791046	Ankush Kadyan	Sales Manager - T4	
RAJIV KUMAR CHOPRA	rajeev@boprealty.com	9411446555	AYUSH SHARMA	BROKER	
RAMESH MANGIRE	RAMESH MANGIRE@BOPREALTY.COM	9205851245	Bhavnesh Kadyan	BROKER	
Ravi Kumar	Ravi.Kumar@boprealty.com	7503635120	AYUSH SHARMA	BROKER	
RAVISH SINGH	ravish.singh@boprealty.com	8210455585	AMIT KADYAN	BROKER	
REHNUMA	kmrahnuma251@gmail.com	8448064223	MANISH SACHDEVA	BROKER	
REPP	REPP@GMAIL.COM	9911177668	Gaurav Mavi	BROKER	
Richa Prashar	prasharricha4@gmail.com	8588803608	Himanshu kumar	Sales Executive - T5	
RICHA SINGH	RICHASINGH9569@GMAIL.COM	9569912052	RISHABH NAGAR	Sales Executive - T5	
Rishabh Dhaka	Rishabhdhakaji@gmail.com	9370511099	Prince Mavi	BROKER	
RISHABH NAGAR	RISHABH.NAGAR18@GMAIL.COM	9599002524	sandeep sethi gurugram	Sales Manager - T4	
RISHI KAPOOR	RISHI KAPOOR@BOPREALTY.COM	9131902789	Bhavnesh Kadyan	BROKER	
Ritesh Berwal	riteshberwal13@gmail.com	8929596869	sandeep sethi gurugram	Sales Executive - T5	
ritika singh	sritikaa50@gmail.com	7607566842	sandeep sethi gurugram	Sales Executive - T5	
Rizwan Ali	rizwan.pasha22@gmail.com	7669423328	SHAMIM KHAN	Team leader - t3	
ROHIT CHAURASIA	ROHITCHAURASIA@boprealty.com	9958058617	RAVISH SINGH	Sales Executive - T5	
Rohit Kapur	rkapur@mag-corp.com	9910033078		Admin	
Rohit Kapur	rohit.external@mailinator.com	9910457990	Admin	TEAM Head - T2	
Rohit Kapur	rkapur@mag-corp.com	9910457575		Admin	
ROHIT magicbricks	rohit@boprealty.com	9560522766	Gaurav Mavi	TEAM Head - T2	
ROHIT SINGH	ROHIT.SINGH@boprealty.com	9650693533	Pratham Verma	Sales Executive - T5	
Rohit Tayal	rohit.tayal@boprealty.com	9818816823	Priyanka Jain	Sales Manager - T4	
Romil Saxena	Romil.saxena@icloud.com	9355876257	Gaurav Mavi	Sales Manager - T4	
saba khan	saba@whiteknights.co.in	9899018540	manik anand	Sales Manager - T4	
Sachin Mavi	sgmc24@gmail.com	7982507208	Gaurav Mavi	TEAM Head - T2	
Sagar Rajput	Sagar Rajput@BOPREALTY.COM	8630728106	AYUSH SHARMA	BROKER	
Sagar Sethi	sagarsethi9927@gmail.com	9540015433	Tarun Virmani	Sales Executive - T5	
Sahil Bhardwaj	SahilBhardwaj@BOPREALTY.COM	9540056338	Puneet Bhardwaj	Sales Executive - T5	
Sahil Kalra	sahilkalra11402@gmail.com	8826093724	Shweta sikdar	Sales Executive - T5	
sahil kassar	sahil.@boprealty.com	9873382565	Vinod singh	Sales Executive - T5	
Saksham Vats	Saksham29032025@gmail.com	7669428058	Yash Sharma	Sales Executive - T5	
SANCHIT DIXIT	SKDIXIT038@GMAIL.COM	6395590625		BROKER	
Sandeep	Sandeep@BOPREALTY.COM	8800420984	RAVISH SINGH	BROKER	
SANDEEP	SANDEEP@boprealty.com	9167388431	MANUPUSHPAM TYAGI	Sales Executive - T5	
sandeep bhardwaj	sandeep@boprealty.com	8800490046	amit mavi	Sales Manager - T4	
Sandeep chaudhary	Sandeepchaudhary@boprealty.com	9990808833	MANUPUSHPAM TYAGI	BROKER	
Sandeep chaudhary	Sandeepchaudhary7058@gmail.com	9058307058	Vishal pandey	Sales Executive - T5	
SANDEEP KASANA	SANDEEP.KASANA@boprealty.com	9927970004	ANKIT NAGAR	Sales Manager - T4	
SANDEEP KUMAR	SANDEEP.KUMAR@BOPREALTY.COM	9716415324	Radhika	Sales Executive - T5	
Sandeep Sethi	sn.sethi@yahoo.com	8742930690	Gaurav Mavi	TEAM Head - T2	
sandeep sethi gurugram	Hitesh@BOPREALTY.COM	7503003000	Gaurav Mavi	TEAM Head - T2	
Sangeeta SHARMA	Sangeeta@BOPREALTY.COM	7838752929	AYUSH SHARMA	BROKER	
Sanjay Sharma	sanjaysharma.palwal@gmail.com	7027359616		BROKER	
Sanjay SINHA	Sanjay.SINHA@boprealty.com	9310006520	AYUSH SHARMA	BROKER	
SANTOSH KUMAR	SANTOSH KUMAR@BOPREALTY.COM	9891945600	Bhavnesh Kadyan	BROKER	
Santosh Shah	shah.zenith1982@gmail.com	8800750337		BROKER	
Satrajeet Neogi	satrajeetniyogi@gmail.com	8527288313	komal sharma	BROKER	
Satyam	Satyam@boprealty.com	9711345220	RAGHU NANDAN	Sales Executive - T5	
saurabha gg	saurabh@boprealty.com	9540953578	MANIISH KUMAR DABREY	Sales Executive - T5	
SAURAV MAVI	Saurav.mavi@boprealty.com	8126084952	Gaurav Mavi	TEAM Head - T2	
Seema 136	Seemanshitanwar9899123@gmail.com	8377879008	Owais Mustafa Khan	Sales Executive - T5	
Shabina Saeed	shebik722@gmail.com	8588819640	Romil Saxena	Team leader - t3	
SHALANI SHARMA	SHALANI@KNOWBLER.IN	8447287247	RAHUL SIRADHANA	BROKER	
SHAMIM KHAN	shamim.khan@boprealty.com	9355916568	GAUTAM GUPTA	Sales Manager - T4	
SHARAD GOEL	SHARAD.GOEL@BOPREALTY.COM	9910963789	Ankush Kadyan	Sales Manager - T4	
shashank prasoon	shashank@boprealty.com	7903768481	Gaurav Mavi	Sales Manager - T4	
Shavez Rizvi	Republic.shavez@gmail.com	7786910557	Mohammad Mehdi	Sales Manager - T4	
sheetal	shetal@boprealty.com	9667522538	chirag jaitley	Sales Manager - T4	
SHIMONA	SHIMONA@boprealty.com	8742929982	gaurav gandhi	Sales Manager - T4	
Shivam	shivamjdc2023@gmail.com	6388235853	GAURAV SHARMA	Sales Executive - T5	
SHIVAM MAVI	SHIVAM.MAVI@boprealty.com	7982722386	Sachin Mavi	Sales Executive - T5	
Shivani sharad	Shivani@boprealty.com	9910969918	SHARAD GOEL	Sales Executive - T5	
Shreesh Agarwal	shreeshagarwal@gmail.com	8052805215	Mohammad Mehdi	Sales Manager - T4	
SHRIKANT	Shrikant@boprealty.com	8826960957	sandeep sethi gurugram	Sales Executive - T5	
Shubham	Shubham@boprealty.com	7838169939	SURAJ GUPTA	Sales Executive - T5	
Shubham bansal	Shubham.bansal@BOPREALTY.COM	9625581922	komal sharma	BROKER	
SHUBHAM SHARMA	SHUBHAMSHARMA@BOPREALTY.COM	7599022239	Pratham Verma	Sales Manager - T4	
shubhankar ghosh	shubhankar@boprealty.com	7838171042	Gaurav Mavi	Sales Manager - T4	
Shweta sikdar	Shwetasikdar2@gmail.com	7982653082	chirag jaitley	Sales Manager - T4	
Shweta Singh	shweta@whiteknights.co.in	7428138927	saba khan	Sales Executive - T5	
SIDHANT SHARMA	SIDHANT.SHARMA@bopraelty.com	8192931320	Vishal pandey	Sales Manager - T4	
SIKANDAR KUMAR	SIKANDAR.KUMAR@boprealty.com	9355371616	SHAMIM KHAN	Sales Manager - T4	
SIMRAN	Simran@boprealty.com	8810358564	chirag jaitley	Sales Executive - T5	
SOHIT KUMAR	SOHIT.KUMAR@boprealty.com	8447106614	Vishesh Sharma	Sales Executive - T5	
SONIKA	SONIKA@BOPREALTY.COM	8595181463	Vishal pandey	Sales Executive - T5	
special_permission_user	special_permission_user@gmail.com	1231231234	Gaurav Mavi	Admin	
special_permission_user 2	special_permission_user2@gmail.com	1231231235	Gaurav Mavi	Admin	
sudha	sudha@boprealty.com	9319319578	chirag jaitley	Sales Executive - T5	
SUDHANSHU JOSHI	ICSJUK@GMAIL.COM	9311070133		BROKER	
Sudhir singh	Sudhir.singh@boprealty.com	9891829562	Ankush Kadyan	Sales Manager - T4	
Sumeet Kumar	SumeetKumar@BOPREALTY.COM	9953576559	Vishal pandey	Sales Executive - T5	
Sumit bansal	sumit.bansal@boprealty.com	9711533567	Commercial  User	Commercial	
Sumit Kasana	sumit.kasana@boprealty.com	7290001073	Rajeev Nagar	Sales Manager - T4	
sunil lucknow team	sunil@boprealty.com	9519153192	Mohammad Mehdi	Sales Manager - T4	
sunil verma	sunil.verma@boprealty.com	9711992052	PRAVEEN MAVI	BROKER	
SURAJ GUPTA	SURAJ.GUPTA@BOPREALTY.COM	9315419620	JATIN SHARMA	Sales Manager - T4	
Suraj Kumar Sharma	Suraj.KumarSharma@boprealty.com	9310919019	NARESH BHATIA	Sales Manager - T4	
Swanpandeep	swanpandeep@boprealty.com	9667040488	Pratham Verma	Sales Manager - T4	
Tahir	tahirkhanalvi@gmail.com	9810559558	GAURAV SHARMA	Sales Executive - T5	
tanu pundir	tanu pundir@BOPREALTY.COM	7065842511	SHARAD GOEL	Sales Executive - T5	
Tarun Srivastava	02bravakayastha@gmail.com	8787010487	sandeep sethi gurugram	Sales Manager - T4	
Tarun Virmani	Tarunvirmani80@gmail.com	8742930329	Sandeep Sethi	Sales Manager - T4	
TUSHAR BHARTI	TUSHARBHARTI@boprealty.com	8377904783	Aryan tomer	Sales Executive - T5	
TUSHAR BHATIA	BHATIATUSHAR2511@GMAIL.COM	7056145678	AMIT KOHLI	Sales Manager - T4	
TUSHAR TYAGI	TUSHAR TYAGI@BOPREALTY.COM	9311903353	Bhavnesh Kadyan	BROKER	
Ujjawal	ujjwalghaziabad@gmail.com	7503532174	GAURAV SHARMA	Sales Executive - T5	
Umesh sharma	umesh.sharma@boprealty.com	7669168522	Aarti sharma	Sales Manager - T4	
VAIBHAV KUMAR	VAIBHAV.KUMAR@BOPREALTY.COM	9625971938	Ankush Kadyan	TEAM Head - T2	
vanshika	vanshika@boprealty.com	7838801358	AJAY PAL SINGH	Sales Executive - T5	
Varun Chahal	varun.chahal@boprealty.com	7290001137	Sachin Mavi	Sales Manager - T4	
vigu mavi	vigu.mavi@boprealty.com	9773620814	amit mavi	Sales Manager - T4	
Vikas Choudhary	investandliquidate@gmail.com	9650555059	SAURAV MAVI	BROKER	
VIKAS KUMAR SINHA	VIKAS.SINHA@GMAIL.COM	8130036651	have on deal	BROKER	
VIKAS SINGH	vikasgautam00005@gmail.com	8802729932	chirag jaitley	Sales Manager - T4	
Vikash	Vikash@boprealty.com	8587973918	Vishesh Sharma	BROKER	
vinit rathore	sonurathore60745926@gmail.com	9310858190	Abhishek Tanwar	BROKER	
Vinod singh	vinod.singh@boprealty.com	9654809090	Ankush Kadyan	Sales Manager - T4	
VIRAJ MAVI	VIRAJ.MAVI@BOPREALTY.COM	9599747756	amit mavi	Sales Manager - T4	
Vishal Choudhary	vitcharles@gmail.com	9873037189	Vikas Choudhary	BROKER	
VISHAL JOSHI	VISHAL.JOSHI@BOPREALTY.COM	9654304903		Admin	
Vishal pandey	pandeyvishal2@gmail.com	9654137504	Gaurav Mavi	BROKER	
VISHAL TYAGI	VISHALTYAGI@BOPREALTY.COM	9773909133	RAGHU NANDAN	Sales Manager - T4	
Vishesh Sharma	vishesh.sharma@mybop.in	7290001068	Bhavnesh Kadyan	Sales Manager - T4	
Yash Sharma	yashhxsh@gmail.com	8585939447	Romil Saxena	Sales Manager - T4	
Yash Singhal	singhalyash017@gmail.com	8000021060	harsh yaduvanshi	Sales Executive - T5	
YASHODA	yashodaraoyashoda5@gmail.com	8383966560	MANISH SACHDEVA	BROKER	
Yatendra	yatendras723@gmail.com	9289335928	GAURAV SHARMA	Sales Executive - T5	
ZAKIR	ZAKIR@BOPREALTY.COM	9205332753	JAGDISH	Sales Manager - T4"""
        
        # Parse the data
        lines = excel_data.strip().split('\n')
        team_members = []
        
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 5:
                    team_members.append({
                        'name': parts[0].strip(),
                        'email': parts[1].strip(),
                        'phone': parts[2].strip(),
                        'parent': parts[3].strip(),
                        'role': parts[4].strip()
                    })
        
        self.stdout.write(f'Parsed {len(team_members)} team members from Excel data')
        
        # Import in multiple passes for hierarchy
        imported_count = 0
        
        # Pass 1: Create top-level members
        for member_data in team_members:
            if not member_data["parent"]:
                user, member, created = self.create_member_with_user(member_data)
                if created:
                    imported_count += 1
                    self.stdout.write(f"Created: {member.name} (user: {user.username})")
        
        # Pass 2-5: Create members with parents
        for pass_num in range(2, 6):
            for member_data in team_members:
                if member_data["parent"] and not TeamMember.objects.filter(email=member_data["email"]).exists():
                    try:
                        parent = TeamMember.objects.get(name__iexact=member_data["parent"])
                        user, member, created = self.create_member_with_user(member_data, parent)
                        if created:
                            imported_count += 1
                            self.stdout.write(f"Pass {pass_num} - Created: {member.name} (user: {user.username})")
                    except TeamMember.DoesNotExist:
                        continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {imported_count} team members with user accounts')
        )
        self.stdout.write(f'Total team members: {TeamMember.objects.count()}')
        self.stdout.write(f'Total users: {User.objects.count()}')
    
    def create_member_with_user(self, member_data, parent=None):
        # Create user account
        username = member_data["name"].split()[0].lower()
        password = member_data["phone"]
        
        # Handle duplicate usernames
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': member_data["email"],
                'first_name': member_data["name"].split()[0],
                'last_name': ' '.join(member_data["name"].split()[1:]) if len(member_data["name"].split()) > 1 else ''
            }
        )
        
        if user_created:
            user.set_password(password)
            user.save()
        
        # Create team member
        member, member_created = TeamMember.objects.get_or_create(
            email=member_data["email"],
            defaults={
                "name": member_data["name"],
                "phone": member_data["phone"],
                "role": member_data["role"],
                "parent_user": parent
            }
        )
        
        return user, member, member_created