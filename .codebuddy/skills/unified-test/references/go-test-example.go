// code/src/mock_test/parking_lot_mock/addPark_test.go
//
// 本文件为标准的 Go 表驱动测试模板
// 供 go-test-adapter 生成测试时参考
//
// 技术栈: go test + testify/mock + testify/assert
// 模式: 表驱动测试 (Table-Driven Tests)

package parking_lot_mock

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
	"gorm.io/gorm"

	// 项目内部引用（根据实际项目调整）
	"project/code/src/common/enum"
	"project/code/src/common/errorCode"
	"project/code/src/common/global"
	dbstruct "project/code/src/common/struct/dbstruct"
	parkSrv "project/code/src/parking_lot/service"
)

// ============================================================
// 初始化函数
// ============================================================

// InitService 使用 Mock 结构体初始化被测服务
// 注意: 先检查项目中是否已有可复用的 Mock 结构体
func InitService() parkSrv.ParkSvrImpl {
	mockHandle := commStruct.Handle{
		Logger: &mocktest.MockLogger{},
	}
	mockOption := commStruct.Option{}
	mockMqMgr := &mocktest.MockMQManager{}
	mockDeviceClient := &MockDeviceService{}
	mockSeatMonitoringService := &MockSeatMonitoringService{}
	mockUpService := &MockUpService{}
	mockDaoMgr := &MockDaoMgr{}

	return parkSrv.ParkSvrImpl{
		Handle:            &mockHandle,
		Option:            &mockOption,
		DeviceClient:      mockDeviceClient,
		UpClient:          mockUpService,
		SeatMonitoringSrv: mockSeatMonitoringService,
		DaoMgr:            mockDaoMgr,
		MqMgr:             mockMqMgr,
	}
}

// ============================================================
// 测试函数
// ============================================================

func TestAddPark(t *testing.T) {
	service := InitService()

	// 辅助函数：创建 int 指针
	intPtr := func(i int) *int {
		return &i
	}

	// ----------------------------------------------------------
	// 定义测试用例
	// ----------------------------------------------------------
	// tests 定义了 TestAddPark 的测试用例结构体数组
	// name:        测试用例名称
	// req:         添加停车场的请求参数
	// setupMock:   Mock 设置函数，用于初始化 Mock 对象的行为
	// expectErr:   期望返回的错误
	// expectCode:  期望返回的状态码
	// description: 测试用例描述（中文）
	// afterTest:   测试后清理函数
	tests := []struct {
		name        string
		req         parkSrv.AddParkRequest
		setupMock   func(*MockDaoMgr, *MockUpService)
		expectErr   error
		expectCode  int
		description string
		afterTest   func()
	}{
		// ======================================================
		// 用例1: 成功创建主停车场（Happy Path）
		// ======================================================
		{
			name: "test AddPark successfully with main park",
			setupMock: func(m *MockDaoMgr, u *MockUpService) {
				global.ParkNum = 100
				// 获取停车场数量
				m.On("CountAllParkNum").Return(int64(5), nil).Maybe()
				// 检查停车场名是否已存在（返回 RecordNotFound 表示不存在）
				m.On("SelectParkIsExistByName", "TestPark").Return(1, gorm.ErrRecordNotFound).Maybe()
				// 获取 DB 并开启事务
				m.On("GetDB").Return(nil).Maybe()
				// 创建停车场
				m.On("CreatePark", mock.Anything, mock.Anything).Return(100, nil).Maybe()
				// 添加默认配置（主停车场 MainParkId == 0）
				m.On("CreateParkConfig", mock.Anything).Return(nil).Maybe()
				// 创建默认收费规则分组
				m.On("CreateDefaultChargeRuleGroup", mock.Anything, 100).Return(nil).Maybe()
				// 添加默认内部车配置
				m.On("SelectParkInfoByIDTx", mock.Anything, 100).
					Return(dbstruct.TblParkingInfo{ID: 100, ParkName: "TestPark", MainParkId: 0}, nil).Maybe()
				m.On("BatchInsertInnerConfig", mock.Anything).Return(nil).Maybe()
				m.On("InsertPackageFeature", mock.Anything).Return(1, nil).Times(4)
				// 云端同步
				global.CloudUse = true
				u.On("DealResourceChangeInnerList", mock.Anything).Return(dafgStruct.CommonResponse{}, nil).Maybe()
			},
			req: parkSrv.AddParkRequest{
				MainParkId:             0,
				ParkName:               "TestPark",
				ParkType:               intPtr(1),
				TotalSpaceNum:          intPtr(100),
				RemainSpaceNum:         intPtr(50),
				ReservedSpaceNum:       intPtr(20),
				RemainReservedSpaceNum: intPtr(10),
				EzParkingFlag:          0,
			},
			expectErr:   nil,
			expectCode:  errorCode.Success.Code,
			description: "成功添加主停车场（完整链路）",
			afterTest: func() {
				global.ParkNum = 0
				global.CloudUse = false
				// 等待协程完成（如果有 go func()）
				time.Sleep(2 * time.Second)
			},
		},

		// ======================================================
		// 用例2: 参数校验失败
		// ======================================================
		{
			name: "test AddPark with invalid params",
			setupMock: func(m *MockDaoMgr, u *MockUpService) {
				// 参数校验失败时不会调用任何 DAO 方法
			},
			req: parkSrv.AddParkRequest{
				// 缺少必填参数，触发校验失败
				ParkName: "",
			},
			expectErr:   errorCode.ErrInvalidParam,
			expectCode:  0,
			description: "参数校验失败 - 缺少停车场名称",
			afterTest:   nil,
		},

		// ======================================================
		// 用例3: 停车场数量超限
		// ======================================================
		{
			name: "test AddPark when park num exceeds limit",
			setupMock: func(m *MockDaoMgr, u *MockUpService) {
				global.ParkNum = 5
				m.On("CountAllParkNum").Return(int64(5), nil).Maybe()
			},
			req: parkSrv.AddParkRequest{
				MainParkId:             0,
				ParkName:               "TestPark",
				ParkType:               intPtr(1),
				TotalSpaceNum:          intPtr(100),
				RemainSpaceNum:         intPtr(50),
				ReservedSpaceNum:       intPtr(20),
				RemainReservedSpaceNum: intPtr(10),
			},
			expectErr:   errorCode.ErrParkNum,
			expectCode:  0,
			description: "停车场数量已达上限",
			afterTest: func() {
				global.ParkNum = 0
			},
		},

		// ======================================================
		// 用例4: 获取停车场数量异常
		// ======================================================
		{
			name: "test AddPark when CountAllParkNum returns error",
			setupMock: func(m *MockDaoMgr, u *MockUpService) {
				global.ParkNum = 100
				m.On("CountAllParkNum").Return(int64(0), errors.New("db error")).Maybe()
			},
			req: parkSrv.AddParkRequest{
				MainParkId:             0,
				ParkName:               "TestPark",
				ParkType:               intPtr(1),
				TotalSpaceNum:          intPtr(100),
				RemainSpaceNum:         intPtr(50),
				ReservedSpaceNum:       intPtr(20),
				RemainReservedSpaceNum: intPtr(10),
			},
			expectErr:   errorCode.ErrFailed,
			expectCode:  0,
			description: "获取停车场数量时数据库异常",
			afterTest: func() {
				global.ParkNum = 0
			},
		},

		// ======================================================
		// 用例5: 停车场名称已存在
		// ======================================================
		{
			name: "test AddPark when park name already exists",
			setupMock: func(m *MockDaoMgr, u *MockUpService) {
				global.ParkNum = 100
				m.On("CountAllParkNum").Return(int64(5), nil).Maybe()
				// 返回 nil error 表示找到了同名停车场
				m.On("SelectParkIsExistByName", "ExistingPark").Return(1, nil).Maybe()
			},
			req: parkSrv.AddParkRequest{
				MainParkId:             0,
				ParkName:               "ExistingPark",
				ParkType:               intPtr(1),
				TotalSpaceNum:          intPtr(100),
				RemainSpaceNum:         intPtr(50),
				ReservedSpaceNum:       intPtr(20),
				RemainReservedSpaceNum: intPtr(10),
			},
			expectErr:   errorCode.ErrParkAlreadyExists,
			expectCode:  0,
			description: "停车场名称已存在",
			afterTest: func() {
				global.ParkNum = 0
			},
		},
	}

	// ----------------------------------------------------------
	// 执行测试用例
	// ----------------------------------------------------------
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建新的 mock 对象（每个用例独立）
			mockDao := &MockDaoMgr{}
			mockUpService := &MockUpService{}

			// 设置 mock 行为
			if tt.setupMock != nil {
				tt.setupMock(mockDao, mockUpService)
			}

			// 将 mock 设置到 service
			service.DaoMgr = mockDao
			service.UpClient = mockUpService

			// 执行测试
			resp, err := service.AddPark(context.Background(), tt.req)

			// 断言结果
			if tt.expectErr != nil {
				assert.Error(t, err)
				assert.Equal(t, tt.expectErr, err)
			} else {
				assert.NoError(t, err)
				assert.Equal(t, tt.expectCode, resp.Code)
			}

			// 测试后清理
			if tt.afterTest != nil {
				tt.afterTest()
			}
		})
	}
}
