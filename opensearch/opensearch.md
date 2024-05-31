# OpenSearch

### **🔹 클러스터 설정**
- OpenSearch 2.13 
- 가용 영역(AZ) 1개
- 인스턴스 유형 : <code>t3.medium.search</code> 10GB 노드 2개
- 노드 수 : 2
- 스토리지 : EBS(범용(SSD) - gp3)), 크기 10GB
- 네트워크 : Public Access
- template : 개발 및 테스트
- 최대 절 수 : 1024

---

### 📌 **Configuration 과정**
1. OpenSearch 도메인 생성
2. fastcampus, codeit, inflearn 인덱스 생성 (매핑 정보는 mappings.yml 파일 참조)
3. s3에서 가져온 json 전처리 후 OpenSearch에 문서 색인하는 람다 함수 작성 (lambda_fuction.py 참조)
4. <code>pip install opensearch-py -t . </code> 로 필요한 패키지 설치
5. <code>zip my-deployment-package.zip .</code> 로 압축
6. AWS Console의 Lambda에서 zip 파일 업로드
7. Lambda에 Trigger로 S3의 버킷 지정
 
---

### 📍 **OpenSearch 관련 추가 설정**
- <code>request filter_path</code> : 응답 크기를 줄이도록
- 필드에 가중치(**boost**) 설정 : 제목에는 3배 가중치, 태그에는 2배 가중치 부여