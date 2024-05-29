# IT/소프트웨어 강의 통합 검색 사이트
<div align="center">
<img src="https://github.com/myeunee/DE_Integrated-Search-Website-for-Spark-based-IT-Software-Courses/assets/111333350/0938eb9c-8f4e-4111-9e6d-ddc0c2d8b4a4" alt="IT/소프트웨어 강의 통합 검색 사이트" width="600"/>
  <br>
    <br>
<p align="center">
   <img src="https://img.shields.io/badge/Apache_Spark-E5426E?style=flat-square&logo=Apache Spark&logoColor=white" alt="Apache Spark badge">
   <img src="https://img.shields.io/badge/Apache_Airflow-E25A1C?style=flat-square&logo=Apache Airflow&logoColor=white" alt="Apache Airflow badge">
    <img src="https://img.shields.io/badge/Amazon_S3-569A31?style=flat-square&logo=Amazon S3&logoColor=white" alt="Amazon S3 badge">
    <img src="https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat-square&logo=awslambda&logoColor=white" alt="awslambda badge">
      <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="postgresql badge">
    <img src="https://img.shields.io/badge/OpenSearch-5C3EE8?style=flat-square&logo=opensearch&logoColor=white" alt="opensearch badge">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="fastapi badge">
      <img src="https://img.shields.io/badge/Flutter-02569B?style=flat-square&logo=flutter&logoColor=white" alt="flutter badge">
  </p>
</div>

<br>

`FastLearnIt` 은 **Spark와 OpenSearch를 이용한 통합 IT 강의 검색 사이트**입니다.
<br>
>다양한 IT 강의 플랫폼에서 제공하는 강의들을 한 곳에서 쉽게 검색하세요!
>
<br>

## 📌 Preview
<br>
<영상>
  
>1. 강의의 구성 요소(내용, 리뷰)를 한 눈에 비교
>2. 사용자의 강의 탐색 시간을 줄여 학습의 효율성을 높임
>3. 가격 및 할인 혜택을 비교하여 합리적인 가격에 선택

<br>

## ⌘ Project BackGround
![image](https://github.com/khuda-5th/DE_Integrated-Search-Website-for-Spark-based-IT-Software-Courses/assets/111333350/a71d9871-7430-4e3b-8a54-4142abf1ad6d)



* **`배경`** : IT 강의 수요 증가로 인한 온라인 교육 플랫폼 시장이 넓어졌다. 그러나 이러한 풍부한 자료의 양은 오히려 사용자가 필요한 강의를 선택하는 데 혼란을 야기한다.

* **`목표`** : 선택의 다양성을 제공하는 동시에, 학습자에게 통합된 자료를 제공하자.


## ⚙️ Service Architecture
![image](https://github.com/myeunee/DE_Integrated-Search-Website-for-Spark-based-IT-Software-Courses/assets/111333350/0d854869-1365-43b9-a64c-dad1340e2d5a)

<br>

### 1️⃣ Airflow DAG 구성을 통해 자동 크롤링

![image](https://github.com/khuda-5th/DE_Integrated-Search-Website-for-Spark-based-IT-Software-Courses/assets/111333350/da9e9f66-980a-4525-a740-753ebb7c9355)

>- 신규 강의에 대한 정보를 가져오기 위해 Airflow로 주기적인 크롤링을 한다.
>- EC2 인스턴스를 생성한 후, 각 강의 사이트를 크롤링 및 전처리한 데이터를 S3에 업로드한다.

<br>

### 2️⃣ Airflow DAG 구성을 통해 자동 크롤링

### 3️⃣ Airflow DAG 구성을 통해 자동 크롤링

## 🤗 Members
| 김건형 | 노명은 | 박상영 | 유혜지 |
| :-: | :-: | :-: | :-: |
| <img src='https://avatars.githubusercontent.com/u/60197194?v=4' height=130 width=130></img> |  <img src='https://avatars.githubusercontent.com/u/90135669?v=4' height=130 width=130></img> | <img src='https://avatars.githubusercontent.com/u/107484383?s=96&v=4' height=130 width=130></img> | <img src='https://avatars.githubusercontent.com/u/90139122?v=4' height=130 width=130></img> |
| <a href="https://github.com/g-hyeong" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/NoMyeongEun" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/Imsyp" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/HyejiYu" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> |



| 윤소은 | 이소연 | 한상진 | 허윤지 |
| :-: | :-: | :-: | :-: |
| <img src='https://avatars.githubusercontent.com/u/160216493?s=96&v=4' height=130 width=130></img> | <img src='https://avatars.githubusercontent.com/u/84007823?s=96&v=4' height=130 width=130></img> | <img src='https://avatars.githubusercontent.com/u/49024115?v=4' height=130 width=130></img> | <img src='https://avatars.githubusercontent.com/u/111333350?v=4' height=130 width=130></img> |
| <a href="https://github.com/Younsoeun" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/soyeon-kk" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/eu2525" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/myeunee" target="_blank"><img src="https://img.shields.io/badge/GitHub-black.svg?&style=round&logo=github"/></a> |

<br>
